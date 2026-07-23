import re
import uuid
from typing import Dict, Any
from desktop.models.identity import CommandIdentity, Resolver

class CommandResolver(Resolver[str, CommandIdentity]):
    """
    Normalizes raw terminal commands into generic identities and categories (Rule 47).
    Applies deterministic redaction for sensitive commands (Rule 45).
    """
    
    @staticmethod
    def redact_command(raw_command: str) -> str:
        """Removes secrets from common CLI commands"""
        redacted = raw_command
        
        # Redact generic flags (-p, --password)
        redacted = re.sub(r'(--password|-p)\s+["\']?[^\s"\'=]+["\']?', r'\1 <REDACTED>', redacted, flags=re.IGNORECASE)
        redacted = re.sub(r'(--password|-p)=["\']?[^\s"\']+["\']?', r'\1=<REDACTED>', redacted, flags=re.IGNORECASE)
        
        # Redact curl basic auth (curl -u user:pass)
        redacted = re.sub(r'(-u|--user)\s+([^:\s]+):[^\s]+', r'\1 \2:<REDACTED>', redacted)
        
        # Redact URL credentials (https://user:pass@github.com)
        redacted = re.sub(r'(https?://)([^:\s]+):[^@\s]+@', r'\1\2:<REDACTED>@', redacted)
        
        # AWS/Azure/Docker/SSH
        redacted = re.sub(r'(aws_access_key_id|aws_secret_access_key)=[\w/+=]+', r'\1=<REDACTED>', redacted, flags=re.IGNORECASE)
        redacted = re.sub(r'(docker login.*-p\s+)[^\s]+', r'\1<REDACTED>', redacted)
        
        return redacted

    def resolve(self, raw_command: str) -> CommandIdentity:
        redacted = CommandResolver.redact_command(raw_command)
        parts = redacted.strip().split()
        if not parts:
            cp = "unknown"
            return CommandIdentity(
                id=f"cmd_{uuid.uuid5(uuid.NAMESPACE_URL, cp).hex[:8]}",
                type="COMMAND",
                display_name=cp,
                canonical_path=cp,
                category="UNKNOWN",
                metadata={"raw": redacted, "args": []}
            )
            
        base_cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        identity = base_cmd
        category = "SYSTEM"
        
        if base_cmd == "git":
            category = "GIT"
            if args:
                identity = f"git {args[0]}"
                
        elif base_cmd in ["npm", "yarn", "pnpm"]:
            category = "BUILD"
            if args:
                identity = f"{base_cmd} {args[0]}"
                
        elif base_cmd in ["python", "python3"]:
            category = "PYTHON"
            if args and not args[0].startswith('-'):
                identity = f"python {args[0]}"
                
        elif base_cmd == "pip":
            category = "PACKAGE_MANAGER"
            if args:
                identity = f"pip {args[0]}"
                
        elif base_cmd == "docker":
            category = "CONTAINER"
            if args:
                identity = f"docker {args[0]}"
                
        elif base_cmd == "ssh":
            category = "REMOTE"
            identity = "ssh" # Drop args for ssh identity
            
        elif base_cmd in ["curl", "wget"]:
            category = "NETWORK"
            identity = base_cmd
            
        elif base_cmd in ["cd", "ls", "dir", "mkdir", "rm", "rmdir", "cp", "mv"]:
            category = "FILESYSTEM"
            identity = base_cmd
            
        return CommandIdentity(
            id=f"cmd_{uuid.uuid5(uuid.NAMESPACE_URL, identity).hex[:8]}",
            type="COMMAND",
            display_name=identity,
            canonical_path=identity,
            category=category,
            metadata={"raw": redacted, "args": args}
        )
