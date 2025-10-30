# Time-lapse Video Traffic Analysis

Use time-lapse videos instead of static images for continuous, realistic traffic updates.

## 📁 New Files Created

1. **`timelapse_traffic.py`** - Core time-lapse analyzer module
2. **`traffic_project_timelapse.py`** - Flask app using time-lapse videos
3. **`create_timelapse_videos.py`** - Helper to create videos from your images

## 🚀 Quick Start

### Option 1: Create Videos from Your Existing Images

```powershell
# Step 1: Create time-lapse videos from image variations
python create_timelapse_videos.py
```

This will:

- Use your existing `images/*_v1.png`, `*_v2.png`, `*_v3.png` files
- Create MP4 videos in the `videos/` folder
- Each video loops through the variations 20 times
- 2 FPS (each image shown for 0.5 seconds)

```powershell
# Step 2: Run the time-lapse version
python traffic_project_timelapse.py
```

### Option 2: Use Your Own Time-lapse Videos

If you have actual traffic camera time-lapse footage:

1. **Place videos in `videos/` folder:**

   ```
   videos/
   ├── start_r1_timelapse.mp4
   ├── r1_r2_timelapse.mp4
   ├── r2_r3_timelapse.mp4
   └── ... (other segments)
   ```

2. **Run the application:**
   ```powershell
   python traffic_project_timelapse.py
   ```

## 🎬 How It Works

### Time-lapse Analysis Flow

1. **Load Videos**: System loads MP4 files for each road segment
2. **Extract Frames**: Every API call extracts next frame from each video
3. **Vehicle Counting**: OpenCV analyzes the frame (same algorithm as images)
4. **Auto-loop**: When video ends, it loops back to the beginning
5. **Updates**: Traffic data updates every 5 seconds (faster than 1-minute image mode)

### Frame Interval

```python
TimelapseTrafficAnalyzer(frame_interval=30)
```

- `frame_interval=30` means skip 30 frames between reads
- For 30 FPS video, this gives ~1 frame per second
- Adjust based on your video FPS and desired speed

## ⚙️ Configuration

### In `traffic_project_timelapse.py`:

```python
# Change update frequency (seconds)
if current_time - last_update_time >= 5:  # Change this value
    update_traffic_from_videos()
```

### In `create_timelapse_videos.py`:

```python
create_timelapse_from_images(
    temp_folder,
    output_path,
    fps=2,         # Video frame rate
    loop_count=20  # How many times to repeat images
)
```

## 📊 Advantages Over Static Images

✅ **Smoother updates** - New frame every 5 seconds vs 1 minute  
✅ **More realistic** - Continuous flow simulation  
✅ **Better for demos** - Looks more dynamic  
✅ **Real camera footage** - Can use actual traffic cameras  
✅ **Longer sequences** - Videos can have hundreds of frames

## 🎥 Video Requirements

- **Format**: MP4, AVI, or any OpenCV-supported format
- **Resolution**: Any (system auto-detects)
- **Length**: Any (loops automatically)
- **Recommended**: 30+ seconds at 15-30 FPS

## 🔄 Comparison: Images vs Time-lapse

| Feature          | Static Images          | Time-lapse Videos               |
| ---------------- | ---------------------- | ------------------------------- |
| Update frequency | 1 minute               | 5 seconds                       |
| Data source      | Random image selection | Sequential frames               |
| Setup            | Simple (drop images)   | Moderate (create/record videos) |
| Realism          | Medium                 | High                            |
| File size        | Small (KB per image)   | Larger (MB per video)           |

## 🛠️ Testing

### Test the analyzer standalone:

```powershell
python timelapse_traffic.py
```

This runs a demo that:

- Loads all videos
- Prints vehicle counts every 5 seconds
- Shows which frame is being analyzed
- Press Ctrl+C to stop

### Debug mode:

```python
# In timelapse_traffic.py
analyzer.save_current_frames('temp_frames')
```

This saves current frames to disk so you can see what's being analyzed.

## 📝 Example Workflow

1. **Record or simulate traffic:**

   - Use traffic camera footage
   - OR create from images: `python create_timelapse_videos.py`

2. **Verify videos created:**

   ```powershell
   ls videos/
   ```

   Should show: `*_timelapse.mp4` files

3. **Start the server:**

   ```powershell
   python traffic_project_timelapse.py
   ```

4. **Open React frontend:**

   ```powershell
   cd frontend
   npm start
   ```

5. **Watch real-time updates:**
   - Traffic counts change every 5 seconds
   - Colors update dynamically
   - Best route recalculates

## 🎯 Next Steps

- Record actual traffic camera footage (dashcam, security camera)
- Use longer time-lapse sequences (multiple hours)
- Adjust `frame_interval` for faster/slower progression
- Implement frame caching for better performance
- Add video preprocessing (stabilization, enhancement)

## 🔧 Troubleshooting

**Videos not loading?**

- Check file paths in `video_mapping`
- Verify MP4 codec (use H.264)
- Try re-encoding: `ffmpeg -i input.mp4 -c:v libx264 output.mp4`

**Low vehicle counts?**

- Check frame quality (resolution, brightness)
- Adjust contour area threshold in `count_vehicles_in_frame()`
- Save frames to disk and inspect visually

**Performance issues?**

- Increase `frame_interval` (skip more frames)
- Reduce video resolution
- Use lower FPS videos
