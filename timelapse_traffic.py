"""
Time-lapse Video Traffic Analysis
This module extracts frames from time-lapse videos and uses them for real-time traffic updates
"""
import cv2
import os
import time
from pathlib import Path

class TimelapseTrafficAnalyzer:
    def __init__(self, video_folder='videos', frame_interval=30):
        """
        Initialize the time-lapse analyzer
        
        Args:
            video_folder: Folder containing time-lapse videos for each road segment
            frame_interval: Number of frames to skip between extractions (for speed)
        """
        self.video_folder = video_folder
        self.frame_interval = frame_interval
        self.video_captures = {}
        self.current_frame_indices = {}
        self.total_frames = {}
        
        # Create video folder if it doesn't exist
        os.makedirs(video_folder, exist_ok=True)
        
    def load_videos(self, video_mapping):
        """
        Load time-lapse videos for each road segment
        
        Args:
            video_mapping: Dict mapping segment names to video file paths
                          e.g., {'Start_R1': 'videos/start_r1_timelapse.mp4'}
        """
        print("Loading time-lapse videos...")
        for segment, video_path in video_mapping.items():
            if os.path.exists(video_path):
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    self.video_captures[segment] = cap
                    self.current_frame_indices[segment] = 0
                    self.total_frames[segment] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    print(f"  ✓ Loaded {segment}: {video_path} ({self.total_frames[segment]} frames)")
                else:
                    print(f"  ✗ Failed to open {segment}: {video_path}")
            else:
                print(f"  ✗ Video not found: {video_path}")
                
    def get_next_frame(self, segment):
        """
        Get the next frame from a segment's time-lapse video
        
        Args:
            segment: Road segment name
            
        Returns:
            frame: OpenCV image frame, or None if not available
        """
        if segment not in self.video_captures:
            return None
            
        cap = self.video_captures[segment]
        
        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_indices[segment])
        
        ret, frame = cap.read()
        
        if ret:
            # Move to next frame (with interval)
            self.current_frame_indices[segment] += self.frame_interval
            
            # Loop back to start if we reached the end
            if self.current_frame_indices[segment] >= self.total_frames[segment]:
                self.current_frame_indices[segment] = 0
                print(f"  {segment}: Looping video back to start")
                
            return frame
        else:
            # If read failed, reset to start
            self.current_frame_indices[segment] = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return None
            
    def count_vehicles_in_frame(self, frame):
        """
        Count vehicles in a video frame using contour detection
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            count: Number of vehicles detected
        """
        if frame is None:
            return 0
            
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Edge detection
        edges = cv2.Canny(blur, 80, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by area (vehicles should be reasonably sized)
        vehicles = [cnt for cnt in contours if cv2.contourArea(cnt) > 400]
        
        return len(vehicles)
        
    def get_all_traffic_counts(self):
        """
        Get current traffic counts from all video segments
        
        Returns:
            dict: Mapping of segment names to vehicle counts
        """
        counts = {}
        
        for segment in self.video_captures.keys():
            frame = self.get_next_frame(segment)
            count = self.count_vehicles_in_frame(frame)
            counts[segment] = count
            
        return counts
        
    def save_current_frames(self, output_folder='temp_frames'):
        """
        Save current frames from all videos (useful for debugging)
        
        Args:
            output_folder: Folder to save frames
        """
        os.makedirs(output_folder, exist_ok=True)
        
        for segment in self.video_captures.keys():
            frame = self.get_next_frame(segment)
            if frame is not None:
                filename = f"{output_folder}/{segment}_frame_{self.current_frame_indices[segment]}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved: {filename}")
                
    def close(self):
        """Release all video captures"""
        for cap in self.video_captures.values():
            cap.release()
        print("All video captures released")


# Example usage and integration
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = TimelapseTrafficAnalyzer(video_folder='videos', frame_interval=30)
    
    # Map segments to video files
    # You need to provide time-lapse videos for your road segments
    video_mapping = {
        'Start_R1': 'videos/start_r1_timelapse.mp4',
        'R1_R2': 'videos/r1_r2_timelapse.mp4',
        'R2_R3': 'videos/r2_r3_timelapse.mp4',
        'R3_R4': 'videos/r3_r4_timelapse.mp4',
        'R4_End': 'videos/r4_end_timelapse.mp4',
        'U1_R1': 'videos/u1_r1_timelapse.mp4',
        'U1_R2': 'videos/u1_r2_timelapse.mp4',
        'U2_R3': 'videos/u2_r3_timelapse.mp4',
        'U2_R4': 'videos/u2_r4_timelapse.mp4',
        'L1_R1': 'videos/l1_r1_timelapse.mp4',
        'L1_R2': 'videos/l1_r2_timelapse.mp4',
        'L2_R3': 'videos/l2_r3_timelapse.mp4',
        'L2_R4': 'videos/l2_r4_timelapse.mp4',
        'L1_L2': 'videos/l1_l2_timelapse.mp4',
        'U1_U2': 'videos/u1_u2_timelapse.mp4',
    }
    
    # Load videos
    analyzer.load_videos(video_mapping)
    
    # Simulate continuous traffic monitoring
    print("\nStarting traffic monitoring (Press Ctrl+C to stop)...")
    try:
        while True:
            print(f"\n--- Update at {time.strftime('%H:%M:%S')} ---")
            counts = analyzer.get_all_traffic_counts()
            
            for segment, count in counts.items():
                print(f"  {segment}: {count} vehicles")
                
            # Wait before next update (e.g., 5 seconds)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\nStopping traffic monitoring...")
        analyzer.close()
