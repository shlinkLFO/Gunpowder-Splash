# Collaborative Editing Guide

This document explains how collaborative editing works in the Glowstone IDE across different tabs and file types.

---

## Overview

The IDE provides **two modes of collaborative editing**:

1. **Web-Edit Tab**: Full real-time synchronization (instant updates as you type)
2. **Code Editor Tab**: Save-based synchronization (updates when files are saved)

Both modes use a bidirectional WebSocket server for communication between collaborators.

---

## Web-Edit Tab (Full Real-Time Sync)

### How It Works
- **CSS, JavaScript, HTML quadrants** sync in real-time across all users
- Changes appear within **300ms** of typing
- Live Preview updates automatically for all collaborators
- User presence shows who's connected

### Features
✅ **Instant synchronization** - See changes as others type  
✅ **User presence indicators** - Know who's collaborating  
✅ **Connection status** - Green dot when connected  
✅ **Automatic reconnection** - Handles network interruptions  
✅ **Live Preview sync** - All users see the same preview  

### Best Practices
- Communicate via chat before making major changes
- Work on different quadrants when possible
- Save your work frequently

---

## Code Editor Tab (Save-Based Sync)

### How It Works
- Files sync when you click **"💾 Save File"**
- Other users see a notification when files are updated
- Click **"Reload to see changes"** to refresh the file
- User presence shows who's editing which files

### Features
✅ **Multi-file support** - All file types (.py, .ipynb, .json, .csv, .md, .txt, .cs, .cpp, etc.)  
✅ **Auto-detected syntax highlighting** - 20+ languages supported  
✅ **User presence tracking** - See who's editing what  
✅ **Update notifications** - Know when files change  
✅ **File-level tracking** - Track who has which files open  

### Limitations
⚠️ **Not real-time** - Changes sync only on save, not as you type  
⚠️ **Manual refresh required** - Must reload to see others' changes  
⚠️ **Potential conflicts** - Last save wins (no automatic merging)  

### Best Practices
1. **Save often** - Click "💾 Save File" regularly to share your work
2. **Watch for notifications** - Reload when you see "File updated by user_X"
3. **Communicate** - Let teammates know before editing shared files
4. **Use different files** - Avoid simultaneous edits to the same file
5. **Save before switching** - Always save before changing tabs

---

## Why the Difference?

### Web-Edit: Custom HTML Component
The Web-Edit interface is built with a **custom HTML component** that gives us full control over the editor and WebSocket integration. We can:
- Hook into every keystroke
- Send updates in real-time
- Update the editor programmatically

### Code Editor: Third-Party Component (st_ace)
The Code Editor uses **Streamlit ACE** (st_ace), a third-party component that:
- Runs in an isolated iframe
- Doesn't expose change events to JavaScript
- Cannot be modified programmatically from outside

This is a **limitation of Streamlit's architecture**, not a design choice. To achieve real-time sync in the Code Editor, you would need to:
1. Build a custom ACE wrapper component (major development effort)
2. OR use a different code editor with WebSocket support
3. OR accept save-based synchronization (current approach)

---

## Supported File Types

### Syntax Highlighting
The Code Editor auto-detects and highlights 20+ languages:

- **Programming**: Python (.py), JavaScript (.js), TypeScript (.ts), C++ (.cpp), C# (.cs), Java (.java), Ruby (.rb), Go (.go), Rust (.rs), PHP (.php)
- **Web**: HTML (.html), CSS (.css), JSX (.jsx), TSX (.tsx)
- **Data**: JSON (.json), YAML (.yaml), SQL (.sql), XML (.xml)
- **Markup**: Markdown (.md)
- **Other**: Shell (.sh), Text (.txt)

### Jupyter Notebooks
- `.ipynb` files are supported with cell-by-cell execution
- Markdown cells can be edited inline
- Code cells execute with full Python support
- Collaboration works on the notebook file level

---

## User Presence

### Web-Edit Presence Bar
```
Collaborative Mode:  [user_1] [user_2]  ● Connected
```

Shows:
- All connected users
- Connection status (green = connected, red = disconnected)
- Real-time updates when users join/leave

### Code Editor Presence Bar
```
Collaborative Mode:  [user_1] [user_2]  ● Connected
```

Shows:
- All connected users
- Connection status
- File-level tracking (coming soon: show who's editing which file)

---

## Workflow Examples

### Example 1: Web Development (Web-Edit)
**Scenario**: Building a React component with a team

1. **User 1** opens Web-Edit and starts writing CSS
2. **User 2** joins and sees User 1's CSS instantly
3. **User 2** works on JavaScript while User 1 does CSS
4. **Both** see Live Preview update in real-time
5. **User 3** joins and adds HTML structure
6. All changes sync automatically - no saves needed!

### Example 2: Data Analysis (Code Editor)
**Scenario**: Team analyzing Yelp dataset with Python

1. **User 1** opens `analysis.py` in Code Editor
2. **User 2** sees "user_1 opened file: analysis.py"
3. **User 1** writes analysis code and clicks **"💾 Save File"**
4. **User 2** sees notification: "File updated by user_1"
5. **User 2** clicks **"Reload to see changes"** and sees new code
6. **User 2** adds more code and saves
7. **User 1** reloads to see User 2's additions

### Example 3: Notebook Collaboration
**Scenario**: Creating a Jupyter notebook together

1. **User 1** creates `notebook.ipynb` and adds cells
2. **User 2** opens the same notebook
3. **User 1** saves after adding analysis cells
4. **User 2** reloads and runs the cells
5. Both can execute cells independently
6. Save and reload to share cell changes

---

## Connection Troubleshooting

### WebSocket Not Connecting

**Check Status**: Look at the presence bar
- ● Green dot = Connected ✓
- ● Red dot = Disconnected ✗

**Common Fixes**:
1. **Refresh the page** - Reconnection is automatic
2. **Check network** - Ensure internet connection is stable
3. **Try different browser** - Some corporate networks block WebSockets
4. **Check firewall** - Port 8001 must be accessible

### Server Issues

If the presence bar shows "Offline":

1. **On Replit**: WebSocket server auto-starts with the main app
2. **On glowstone.red**: Ensure websocket service is running:
   ```bash
   sudo systemctl status glowstone-websocket
   sudo systemctl restart glowstone-websocket
   ```

### Files Not Syncing

**Checklist**:
- [ ] Did you click "💾 Save File"?
- [ ] Is the presence bar showing "Connected"?
- [ ] Did the other user click "Reload"?
- [ ] Are you both editing the same file?

---

## Advanced: Technical Details

### WebSocket Message Types

#### Web-Edit Messages
```javascript
// Code update (CSS/JS/HTML)
{
  type: "code_update",
  field: "css" | "javascript" | "html",
  value: "code content",
  user_id: "user_1"
}
```

#### Code Editor Messages
```javascript
// File opened
{
  type: "file_open",
  file_path: "workspace/analysis.py",
  content: "file content"
}

// File updated
{
  type: "file_update",
  file_path: "workspace/analysis.py",
  content: "updated content",
  user_id: "user_2"
}

// File closed
{
  type: "file_close",
  file_path: "workspace/analysis.py"
}
```

#### Presence Messages
```javascript
// User joined
{
  type: "user_joined",
  user: { user_id: "user_3", connected_at: "..." },
  total_users: 3
}

// User left
{
  type: "user_left",
  user_id: "user_2",
  total_users: 2
}
```

### Server State

The WebSocket server maintains:

1. **WEBEDIT_STATE**: Current CSS, JavaScript, HTML content
2. **FILE_STATE**: Content of all open files
3. **FILE_USERS**: Which users have which files open
4. **USER_FILES**: Which files each user has open
5. **USER_CURSORS**: Cursor positions (infrastructure ready)

---

## Future Enhancements

### Planned Features
- [ ] Show which users are editing which specific files
- [ ] Color-coded cursors in Web-Edit
- [ ] Conflict resolution for simultaneous edits
- [ ] Chat integration
- [ ] File locking to prevent conflicts
- [ ] Automatic refresh on file updates
- [ ] Real-time sync for Code Editor (requires custom component)

### How to Contribute
To add real-time sync to Code Editor:
1. Build custom ACE editor component with WebSocket hooks
2. OR use CodeMirror with Yjs for CRDT-based sync
3. OR implement Operational Transformation (OT)

---

## Summary

| Feature | Web-Edit | Code Editor |
|---------|----------|-------------|
| **Real-time sync** | ✅ Yes (instant) | ⚠️ No (save-based) |
| **User presence** | ✅ Yes | ✅ Yes |
| **File types** | CSS/JS/HTML | All types |
| **Syntax highlighting** | Basic | 20+ languages |
| **Notifications** | Live updates | On save |
| **Best for** | Web development | Code editing |

**Recommendation**: 
- Use **Web-Edit** for collaborative web development with instant feedback
- Use **Code Editor** for working with Python, data files, notebooks, and multi-language projects
- Save frequently in Code Editor to share your work
- Communicate with your team to avoid conflicts

---

## Questions?

See also:
- `DEPLOYMENT.md` - How to deploy to glowstone.red
- `SECURITY.md` - Security considerations
- `WEBSOCKET_README.md` - WebSocket server technical docs
- `replit.md` - Full project architecture

Happy collaborating! 🎉
