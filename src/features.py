import re
import dataclasses
import collections

FEATURES_ENABLED = {}
ROLEINFO_PATTERN = re.compile(r"<roleInfo>([\s\S]*)</roleInfo>", re.MULTILINE)
SYSTEM_PATTERN = re.compile(r"<systemPrompt>([\s\S]*)</systemPrompt>", re.MULTILINE)

@dataclasses.dataclass
class RoleInfo:
    user: str = "Human"
    assistant: str = "Assistant"
    system: str = "System"
    developer: str = "System"

@dataclasses.dataclass
class Features:
    role : RoleInfo
    system_prompt: str

def extract_role_info(content : str) -> tuple[RoleInfo, str]:
    if not isinstance(content, str):
        return (RoleInfo(), content)

    if matched := ROLEINFO_PATTERN.search(content):
        roles = {}
        for line in matched.group(1).split("\n"):
            line = line.strip()
            if not line:
                continue
            key, value = line.split(":", 1)
            roles[key.strip().lower()] = value.strip()
        
        return (
            RoleInfo(**roles),
            re.sub(ROLEINFO_PATTERN, "", content)
        )
    
    return (RoleInfo(), content)

def extract_content(content: str, pattern: re.Pattern[str]) -> tuple[str, str]:
    if not isinstance(content, str):
        return content
    
    if matched := pattern.search(content):
        return matched.group(1), content.replace(matched.group(0), "")
    
    return "", content

def process_features(messages : list) -> Features:
    feats = {}

    for k, v in FEATURES_ENABLED.items():
        on = k in messages[0]["content"]
        feats[v] = on
        if on:
            messages[0]["content"] = messages[0]["content"].replace(f"{k}\n", "").replace(k, "")

    role, cont = extract_role_info(messages[0]["content"])
    system, cont = extract_content(cont, SYSTEM_PATTERN)
    messages[0]["content"] = cont
    return Features(role, system, **feats)

async def format_messages(messages: list[dict], role_info: RoleInfo) -> str:
    processed = collections.defaultdict(str)
    for i, msg in enumerate(messages):
        contents = []
        if isinstance(msg["content"], list):
            for cont in msg["content"]:
                if isinstance(cont, str):
                    contents.append(cont)
        else:
            contents.append(msg["content"])
        
        for cont in contents:
            if "<|removeRole|>" in cont:
                cont = cont.replace("<|removeRole|>\n", "").replace(
                    "<|removeRole|>", ""
                )
            else:
                role: str = msg.get("role", "")
                role = getattr(role_info, role.lower(), role_info.system)
                cont = f"\b{role}: {cont}"

            processed[i] += cont + "\n"
        
        processed[i] = processed[i].strip()
    
    processed = [processed[i] for i in sorted(processed.keys())]

    return "\n\n".join(processed)
