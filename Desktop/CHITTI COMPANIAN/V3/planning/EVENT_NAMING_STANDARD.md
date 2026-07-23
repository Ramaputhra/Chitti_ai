# CHITTI Event Naming Standard

**Rule: Never use random event names.**

Every event name must strictly follow the namespace format:
`<Domain>.<Action>` or `<Domain>.<SubDomain>.<Action>`

### 1. Domain
The high-level architectural domain.
- `Application`
- `Configuration`
- `Logging`
- `Theme`
- `Voice`
- `Memory`
- `Hardware`

### 2. Action
The past-tense or present-participle action.
- `Starting`
- `Started`
- `Loaded`
- `Changed`
- `Received`
- `Stopped`
- `Connected`

### Examples
- `Application.Starting`
- `Configuration.Loaded`
- `Theme.Changed`
- `Voice.Received`
- `Memory.Stored`
- `Hardware.Connected`

### Communication Patterns
If an event represents a specific communication pattern (Command, Request, Response), its type should reflect that via the Event Object's `type` field, while the ID remains standard, OR specific suffixes can be used:
- `Theme.ChangeCommand`
- `Theme.GetRequest`
- `Theme.GetResponse`
