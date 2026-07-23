# CHITTI Event Catalog

This document establishes the canonical list of standard event IDs emitted over the Event Bus.
Avoid inventing ad-hoc strings in code; instead, add them here and to `desktop.constants.events`.

## Application Lifecycle
- `Application.Starting`
- `Application.Started`
- `Application.Stopping`
- `Application.Exit`

## Configuration
- `Configuration.Loaded`
- `Configuration.Changed`
- `Configuration.Reloaded`

## Settings
- `Settings.Changed`

## State
- `State.Changed`

## Logging
- `Logging.Initialized`

## Theme
- `Theme.Changed`

## Hardware & Connections
- `Hardware.Connected`
- `Hardware.Disconnected`
- `Network.Online`
- `Network.Offline`

## Voice
- `Voice.DeviceChanged`
- `Voice.CaptureStarted`
- `Voice.CaptureStopped`
- `Voice.AudioFrame`
- `Voice.SpeechStarted`
- `Voice.SpeechEnded`
- `Voice.AudioReady`
- `Voice.PlaybackStarted`
- `Voice.PlaybackFinished`
- `Voice.Error`

## Language
- `Language.TextRecognized`
- `Language.ProcessingStarted`
- `Language.ProcessingFinished`

## Intent
- `Intent.Detected`
- `Intent.Ignored`

## Workflow
- `Workflow.Created`
- `Workflow.Started`
- `Workflow.Completed`

## Response
- `Response.Generated`

## Memory
- `Voice.Stopped`
- `Voice.Received`
- `Audio.OutputStarted`
- `Audio.OutputStopped`

## Conversation & Intent
- `Message.Received`
- `Message.Sent`
- `Intent.Detected`
- `Intent.Rejected`

## Memory
- `Memory.Stored`
- `Memory.Deleted`
- `Memory.Accessed`

## Plugins
- `Plugin.Loaded`
- `Plugin.Failed`
