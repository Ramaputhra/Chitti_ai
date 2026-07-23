import os
import sys

def create_mock_gif(filepath, text, color):
    """
    Creates a simple animated GIF using PIL.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL is not installed. Please install pillow.")
        sys.exit(1)
        
    frames = []
    width, height = 200, 200
    for i in range(10):
        # Create a new image with transparent background
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a bouncing circle
        y_offset = (i % 5) * 10
        circle_box = [50, 50 + y_offset, 150, 150 + y_offset]
        draw.ellipse(circle_box, fill=color)
        
        # Draw text
        try:
            # Fallback font
            font = ImageFont.load_default()
        except Exception:
            font = None
            
        draw.text((70, 160), text, fill="white", font=font)
        frames.append(img)
        
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    frames[0].save(
        filepath,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        disposal=2 # clear frame before rendering next
    )
    print(f"Created mock asset: {filepath}")

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "desktop", "assets", "avatar", "classic"))
    os.makedirs(root_dir, exist_ok=True)
    
    # State mapping
    states = {
        "idle.gif": ("IDLE", (100, 100, 100, 255)),
        "thinking.gif": ("THINK", (0, 0, 255, 255)),
        "speaking.gif": ("SPEAK", (0, 255, 0, 255)),
        "celebrating.gif": ("YAY", (255, 255, 0, 255)),
        "warning.gif": ("WARN", (255, 165, 0, 255)),
        "error.gif": ("ERR", (255, 0, 0, 255))
    }
    
    for filename, (text, color) in states.items():
        filepath = os.path.join(root_dir, filename)
        create_mock_gif(filepath, text, color)
        
    # Also generate the profile.yaml
    profile_path = os.path.join(root_dir, "profile.yaml")
    yaml_content = """name: classic
version: 1.0

states:
  idle:
    asset: idle.gif
    loop: true
    minimum_duration_ms: 800

  thinking:
    asset: thinking.gif
    loop: true
    minimum_duration_ms: 1200

  speaking:
    asset: speaking.gif
    loop: true
    minimum_duration_ms: 0

  celebrating:
    asset: celebrating.gif
    loop: false
    minimum_duration_ms: 2000

  warning:
    asset: warning.gif
    loop: false
    minimum_duration_ms: 1000

  error:
    asset: error.gif
    loop: true
    minimum_duration_ms: 3000
"""
    with open(profile_path, "w") as f:
        f.write(yaml_content)
    print(f"Created profile.yaml at {profile_path}")

if __name__ == "__main__":
    main()
