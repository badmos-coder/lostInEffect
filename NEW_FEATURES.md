# New Automated Features Documentation

## ⚠️ Important Clarification
**This system encrypts INDIVIDUAL FILES within a folder, not the folder as a single unit.**
Each file becomes its own separate `.encrypted` file with its own `.keys` file.

## Overview
Added comprehensive automated encryption and file handling capabilities to the Dilithium quantum-resistant encryption system. The system processes folders by finding all files within them and encrypting each file individually. All new features are implemented in a separate "Automated Mode" tab, leaving the original "Manual Mode" interface completely untouched.

## 🚀 New Features Added

### 1. **Automated Mode Tab**
- Completely separate from the original interface
- Two sub-tabs: "Message Automation" and "Batch File Operations"
- Automatic key generation integration
- Real-time progress tracking

### 2. **Message Automation**
- **Auto Encrypt & Store**: Automatically generates keys and encrypts messages to local JSON files
- **Auto Encrypt & Send**: Automatically generates keys and encrypts/sends messages over network
- **Auto Key Generation Toggle**: Enable/disable automatic key generation for each operation
- **Progress Feedback**: Real-time status updates and operation logs

### 3. **Batch File Operations** *(Important: Individual File Encryption)*
- **Encrypt All Files in Folder**: Finds and encrypts each individual file within a selected folder
- **Decrypt All Files in Folder**: Decrypts all .encrypted files found in a folder
- **Individual File Processing**: Each file becomes a separate .encrypted file with its own .keys file
- **Batch Processing**: Handles multiple files with progress tracking for each file
- **File Structure Preservation**: Maintains original folder structure in the destination
- **Comprehensive Logging**: Detailed operation summaries and error reporting per file

### 4. **File Encryption Manager** (`dilithium/file_operations.py`)
- **FileEncryptionManager Class**: Handles all individual file and batch operations
- **Recursive Folder Scanning**: Automatically finds all files in subdirectories
- **Individual File Encryption**: Each file is encrypted separately (not as a folder unit)
- **JSON-based Encrypted Files**: Each file stored as structured .encrypted JSON file
- **Per-File Key Management**: Each file gets its own .keys file (or shared keys for batch)
- **Progress Callbacks**: Real-time progress updates for UI integration
- **Error Handling**: Robust error handling with detailed error reporting per file

## 🔧 Technical Implementation

### File Structure
```
dilithium/
├── file_operations.py     # New: File encryption manager
├── gui.py                 # Reverted to original state
└── ...                    # Other existing files

example.py                 # Enhanced: Main GUI with new automated features
test_gui.py               # New: Test script for verification
NEW_FEATURES.md           # New: This documentation
```

### Key Components

#### 1. FileEncryptionManager
```python
class FileEncryptionManager:
    - encrypt_file(file_path, output_dir, keys)
    - decrypt_file(encrypted_file_path, output_dir)
    - encrypt_folder(input_folder, output_folder, auto_generate_keys=True)
    - decrypt_folder(encrypted_folder, output_folder)
    - get_files_in_folder(folder_path)
    - set_callbacks(progress_callback, status_callback)
```

#### 2. Enhanced GUI Structure
```
Main Window
├── Manual Mode Tab (Original - Untouched)
│   ├── Key Generation
│   ├── Message Input
│   ├── File Selection
│   ├── Network Transmission
│   └── Output Display
├── Automated Mode Tab (NEW)
│   ├── Message Automation
│   │   ├── Auto Key Generation Toggle
│   │   ├── Message Input
│   │   ├── Auto Encrypt & Store Button
│   │   ├── Auto Encrypt & Send Button
│   │   └── Operation Output
│   └── Batch File Operations
│       ├── Source Folder Selection (files to encrypt)
│       ├── Destination Folder Selection (for encrypted files)
│       ├── How It Works Info Panel
│       ├── Encrypt All Files in Folder Button
│       ├── Decrypt All Files in Folder Button
│       ├── Progress Bar & Status
│       └── Operation Output
└── Monitoring Tab (Original - Untouched)
```

## 📋 How to Use

### Message Automation
1. Navigate to **Automated Mode** → **Message Automation**
2. Ensure **"Automatically generate keys for each operation"** is checked
3. Enter your message in the text area
4. Click **"Auto Encrypt & Store"** to save locally or **"Auto Encrypt & Send"** to transmit

### Batch File Operations (Individual File Encryption)
1. Navigate to **Automated Mode** → **Batch File Operations**
2. Click **"Browse..."** next to **Source Folder** and select folder containing files to encrypt
3. Click **"Browse..."** next to **Destination Folder** and select where encrypted files should be saved
4. Review the "How it works" info panel to understand the process
5. Click **"Encrypt All Files in Folder"** to start encrypting each file individually
6. Monitor progress in the status bar and output window - you'll see each file being processed

### Individual File Decryption
1. Select a folder containing `.encrypted` files as the source folder
2. Select destination folder for decrypted files
3. Click **"Decrypt All Files in Folder"** - each .encrypted file will be decrypted back to its original form

## 🔍 What Actually Happens (Step by Step)

When you use **"Encrypt All Files in Folder"**:

1. **📂 Folder Scanning**: System scans the selected source folder recursively
2. **📄 File Discovery**: Finds all individual files (including files in subfolders)
3. **🔑 Key Generation**: Generates encryption keys (once per batch operation)
4. **🔒 Individual Processing**: For each file found:
   - Reads the file content
   - Encrypts the content using Dilithium quantum-resistant encryption
   - Creates a `.encrypted` JSON file containing the encrypted data
   - Creates a `.keys` file containing the encryption keys
   - Preserves the file's location in the folder structure
5. **📊 Progress Tracking**: Shows real-time progress for each file being processed
6. **📋 Summary Generation**: Creates an `encryption_summary.json` with operation details

**Example**: If you have a folder with:
```
MyDocuments/
├── document.txt
├── photo.jpg
└── subfolder/
    └── data.csv
```

You'll get:
```
EncryptedOutput/
├── document.txt.encrypted
├── document.txt.keys
├── photo.jpg.encrypted
├── photo.jpg.keys
├── subfolder/
│   ├── data.csv.encrypted
│   └── data.csv.keys
└── encryption_summary.json
```

## 📁 File Format

### Encrypted File Structure (.encrypted)
```json
{
  "ciphertext": "hex_encoded_ciphertext",
  "nonce": "hex_encoded_nonce",
  "signature": {
    "mu": "hex_encoded_mu",
    "z": [array_of_signature_values]
  },
  "original_filename": "filename.ext",
  "encrypted_at": "2024-01-01T12:00:00",
  "file_size": 1024
}
```

### Key File Structure (.keys)
```json
{
  "public_key": {
    "seed": "hex_encoded_seed",
    "t": [array_of_public_key_values]
  },
  "private_key": {
    "seed": "hex_encoded_seed",
    "s1": [array_of_secret_values],
    "s2": [array_of_secret_values],
    "t": [array_of_public_key_values]
  }
}
```

### Encryption Summary (encryption_summary.json)
```json
{
  "encryption_completed_at": "2024-01-01T12:00:00",
  "input_folder": "/path/to/input",
  "output_folder": "/path/to/output",
  "total_files": 10,
  "successful_encryptions": 9,
  "failed_encryptions": 1,
  "auto_generated_keys": true,
  "results": [...]
}
```

## ⚡ Performance Features

- **Threading**: All batch operations run in separate threads to keep UI responsive
- **Progress Tracking**: Real-time progress bars and status updates
- **Memory Efficient**: Processes files individually to handle large folders
- **Error Recovery**: Continues processing even if individual files fail
- **Comprehensive Logging**: Detailed logs for debugging and audit trails

## 🔐 Security Features

- **Automatic Key Generation**: Fresh keys for each operation when enabled
- **Quantum-Resistant**: Uses Dilithium post-quantum cryptography
- **Signature Verification**: All encrypted files include and verify digital signatures
- **Structured Storage**: Keys and encrypted data stored securely in JSON format
- **Audit Trail**: Comprehensive logging of all operations

## 🧪 Testing

Run the test script to verify all components:
```bash
python test_gui.py
```

Launch the enhanced GUI:
```bash
python example.py
```

## 📝 Notes

- Original "Manual Mode" interface remains completely unchanged
- All new features are contained within the "Automated Mode" tab
- **Individual File Encryption**: Each file in a folder is encrypted separately, not as a single unit
- Each file becomes its own `.encrypted` file with corresponding `.keys` file
- Folder structure is preserved in the destination (subfolders are maintained)
- Keys are automatically generated and saved with each encrypted file or shared across the batch
- Progress tracking provides real-time feedback showing each file being processed
- All operations are logged for audit and debugging purposes

## 🎯 Benefits

1. **Individual File Control**: Each file is encrypted separately, allowing selective decryption
2. **Ease of Use**: One-click encryption for all files within a folder
3. **Automation**: No manual key management required
4. **Scalability**: Handles large numbers of files efficiently with per-file processing
5. **Reliability**: Robust error handling - if one file fails, others continue processing
6. **Security**: Quantum-resistant encryption with automatic key generation per operation
7. **Transparency**: Real-time progress showing each individual file being processed
8. **Flexibility**: Encrypted files can be moved, shared, or decrypted individually
9. **Compatibility**: Works alongside existing manual features 