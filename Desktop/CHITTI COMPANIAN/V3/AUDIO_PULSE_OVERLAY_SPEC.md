# VIZZU Audio Pulse Overlay Specification

## Overview
A minimal, glowing white audio pulse indicator that appears at the center-bottom of the avatar/presence window when audio is being captured. The pulse reacts in real-time to incoming audio levels.

---

## 🎨 Visual Design

### Shape & Style
- **Type:** Horizontal audio waveform/pulse bar
- **Position:** Centered at bottom of avatar window, 20px from bottom edge
- **Width:** 60% of avatar window width
- **Height:** 4px (idle), 8px (active audio)
- **Color:** White (#FFFFFF) with soft glow
- **Opacity:** 70% center → 0% edges (gradient fade)

### Visual Effect
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                    [AVATAR]                         │
│                                                     │
│                                                     │
│        ░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░             │
│              ↑                                      │
│         Audio Pulse (center-bottom)                 │
│         White glow, edge fade                      │
└─────────────────────────────────────────────────────┘
```

### Pulse Animation
| State | Height | Opacity | Animation |
|-------|--------|---------|-----------|
| Idle/Silent | 2px | 30% | Slow pulse (2s cycle) |
| Active Audio | 4-8px | 70-100% | Reactive to audio level |
| Processing | 3px | 50% | Steady |

### Glow Effect
- **Inner glow:** White (#FFFFFF)
- **Outer glow:** Soft white with blur (8px blur radius)
- **Gradient:** 
  - Center: 100% opacity
  - Edges: 0% opacity (smooth fade)

---

## 🔧 Implementation Specification

### CSS (For Web/HTML Renderer)
```css
.audio-pulse-overlay {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 4px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.3) 20%,
        rgba(255, 255, 255, 0.9) 50%,
        rgba(255, 255, 255, 0.3) 80%,
        transparent 100%
    );
    border-radius: 2px;
    box-shadow: 
        0 0 8px rgba(255, 255, 255, 0.8),
        0 0 16px rgba(255, 255, 255, 0.4);
    transition: height 0.1s ease-out, opacity 0.15s ease-out;
    pointer-events: none;
}

/* Active audio state */
.audio-pulse-overlay.active {
    height: 8px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.5) 20%,
        rgba(255, 255, 255, 1.0) 50%,
        rgba(255, 255, 255, 0.5) 80%,
        transparent 100%
    );
    box-shadow: 
        0 0 12px rgba(255, 255, 255, 1.0),
        0 0 24px rgba(255, 255, 255, 0.6);
}

/* Idle state */
.audio-pulse-overlay.idle {
    height: 2px;
    opacity: 0.5;
    animation: idlePulse 2s ease-in-out infinite;
}

@keyframes idlePulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.6; }
}
```

### Python/Qt (For PySide6)
```python
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QRectF
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QRadialGradient

class AudioPulseOverlay(QWidget):
    """
    Minimal audio pulse indicator at center-bottom of avatar.
    White glow, fades at edges, reacts to audio levels.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._height = 4
        self._opacity = 0.7
        
        # Position: center-bottom, 20px from edge
        self._width_ratio = 0.6  # 60% of parent width
        
    def update_audio_level(self, level: float):
        """
        Update pulse based on audio level (0.0 to 1.0)
        """
        # Height scales from 4px (level 0) to 12px (level 1)
        self._height = 4 + (level * 8)
        # Opacity scales from 0.3 to 1.0
        self._opacity = 0.3 + (level * 0.7)
        self.update()
    
    def set_idle(self):
        """Set to idle animation state"""
        self._height = 2
        self._opacity = 0.3
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        width = int(self.width() * self._width_ratio)
        height = int(self._height)
        x = (self.width() - width) // 2
        y = self.height() - 20 - height
        
        # Create gradient with edge fade
        gradient = QLinearGradient(x, 0, x + width, 0)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.2, QColor(255, 255, 255, int(255 * self._opacity * 0.4)))
        gradient.setColorAt(0.5, QColor(255, 255, 255, int(255 * self._opacity)))
        gradient.setColorAt(0.8, QColor(255, 255, 255, int(255 * self._opacity * 0.4)))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        # Draw main pulse with glow
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(x, y, width, height, height // 2)
        
        # Draw outer glow
        glow_gradient = QLinearGradient(x, 0, x + width, 0)
        glow_gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        glow_gradient.setColorAt(0.3, QColor(255, 255, 255, int(80 * self._opacity)))
        glow_gradient.setColorAt(0.5, QColor(255, 255, 255, int(150 * self._opacity)))
        glow_gradient.setColorAt(0.7, QColor(255, 255, 255, int(80 * self._opacity)))
        glow_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        glow_height = height + 8
        glow_y = y - 4
        painter.setBrush(glow_gradient)
        painter.drawRoundedRect(x, glow_y, width, glow_height, glow_height // 2)
```

### JavaScript (For Web Avatar)
```javascript
class AudioPulseOverlay {
    constructor(container) {
        this.container = container;
        this.element = document.createElement('div');
        this.element.className = 'audio-pulse-overlay idle';
        this.container.appendChild(this.element);
        
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
    }
    
    startListening(audioContext, stream) {
        this.audioContext = audioContext;
        this.analyser = audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
        
        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.element.classList.remove('idle');
        this.element.classList.add('active');
        
        this.animate();
    }
    
    animate() {
        if (!this.analyser) return;
        
        this.analyser.getByteFrequencyData(this.dataArray);
        
        // Calculate average audio level
        const average = this.dataArray.reduce((a, b) => a + b) / this.dataArray.length;
        const normalizedLevel = average / 255;
        
        // Update pulse height and opacity
        const height = 4 + (normalizedLevel * 8);
        const opacity = 0.3 + (normalizedLevel * 0.7);
        
        this.element.style.height = `${height}px`;
        this.element.style.opacity = opacity;
        
        requestAnimationFrame(() => this.animate());
    }
    
    stopListening() {
        this.analyser = null;
        this.element.classList.remove('active');
        this.element.classList.add('idle');
    }
}
```

---

## 📐 Dimensions & Positioning

### Responsive Sizing
| Avatar Window Width | Pulse Width (60%) | Position from Bottom |
|--------------------|--------------------|---------------------|
| 300px | 180px | 20px |
| 400px | 240px | 20px |
| 500px | 300px | 25px |
| 600px | 360px | 25px |

### Height States
| State | Height |
|-------|--------|
| Idle | 2px |
| Normal | 4px |
| Active Audio | 6-12px (dynamic) |

---

## 🎬 Animation Specifications

### Idle Pulse Animation
- **Cycle:** 2 seconds
- **Effect:** Opacity oscillates 0.3 → 0.6 → 0.3
- **Easing:** ease-in-out

### Audio Reactive Animation
- **Update Rate:** 60 FPS (tied to audio frame rate)
- **Rise Time:** 50ms (fast attack)
- **Fall Time:** 150ms (slow decay)
- **Peak Height:** 12px at maximum audio level

### Fade Transitions
- **Appear:** 200ms fade-in
- **Disappear:** 300ms fade-out
- **State Change:** 150ms transition

---

## 🎨 Color Palette

| Element | Color | RGBA |
|---------|-------|------|
| Pulse Center | Pure White | (255, 255, 255, 1.0) |
| Pulse Edge | Transparent | (255, 255, 255, 0.0) |
| Glow Inner | White | (255, 255, 255, 0.8) |
| Glow Outer | Soft White | (255, 255, 255, 0.4) |

---

## 📱 Integration Points

### Event Integration
```python
# Events to listen for:
- "AUDIO_LEVEL_UPDATE" - Real-time audio level (0.0-1.0)
- "SPEECH_STARTED" - Show pulse
- "SPEECH_STOPPED" - Hide pulse
- "LISTENING_ACTIVE" - Show active pulse
- "SLEEPING" - Hide pulse
```

### Component Hierarchy
```
┌─────────────────────────────────────────┐
│         PresenceWindow                  │
│  ┌─────────────────────────────────┐    │
│  │      AvatarWidget                │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │   [Avatar Animation]   │    │    │
│  │  └─────────────────────────┘    │    │
│  │                                 │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │  [AudioPulseOverlay]   │    │    │  ← Center bottom
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist for Implementation

### Design
- [ ] White gradient pulse bar (centered, bottom)
- [ ] Edge fade effect (smooth gradient to transparent)
- [ ] Soft glow effect (box-shadow / blur)
- [ ] Responsive sizing (60% of avatar width)

### Animation
- [ ] Idle pulse animation (2s cycle)
- [ ] Audio reactive height (4-12px)
- [ ] Smooth transitions (CSS or Qt animation)

### Integration
- [ ] Audio level input from VAD/adapter
- [ ] State management (idle/active/silent)
- [ ] Event subscription (LISTENING, SPEECH_STOPPED, etc.)

---

*Created for VIZZU AI Companion - 2026*
