# Quick Setup Guide - Liveness Detection

## Installation (5 minutes)

### Step 1: Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

### Step 2: Install Required Dependency

```powershell
pip install scipy
```

That's it! The liveness detection is now active.

---

## Optional: Enhanced Accuracy (dlib)

If you want the best blink detection accuracy, install dlib:

```powershell
pip install cmake
pip install dlib
```

**Note**: dlib installation can be tricky on Windows. If it fails, don't worry - the system works fine without it using simplified detection methods.

---

## Testing

### Quick Test

```powershell
python test_liveness.py
```

Follow the on-screen instructions:
1. Show your real face → Should see GREEN box
2. Show a printed photo → Should see RED box
3. Test with multiple people → All should be detected

### Full Integration Test

1. Run the main application: `python main.py`
2. Login as Teacher
3. Start a class session
4. Launch face recognition
5. Test with real faces and photos

---

## What Happens Now?

When face recognition runs:

- ✅ **Real faces**: Green box with "LIVE" → Attendance marked
- ❌ **Photos/screens**: Red box with "PHOTO/SCREEN?" → Attendance NOT marked
- 💡 **Instructions displayed**: "Liveness: Blink or move slightly"

---

## Troubleshooting

### "Observing... (need 1 sec)"
**Normal behavior** - Stand still for 1 second, blink naturally

### Real face rejected
- Ensure good lighting
- Face the camera directly
- Blink a few times
- Move head slightly

### Photo passing as real
- Ensure photo isn't being moved
- Check camera quality
- Consider installing dlib

---

## Summary

✅ Zero configuration needed - works out of the box
✅ Only requires `scipy` (automatically uses simplified detection)
✅ Optional dlib for enhanced accuracy
✅ No changes to database or existing functionality
✅ Multiple faces supported simultaneously

**You're ready to go!** The system will now block photo-based spoofing attempts.

For detailed documentation, see `LIVENESS_DETECTION.md`
