import os
import shutil
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import threading
import time
from datetime import datetime

class FileEncryptionManager:
    """Handles file and folder encryption operations"""
    
    def __init__(self, hybrid_system):
        self.hybrid_system = hybrid_system
        self.progress_callback = None
        self.status_callback = None
        
    def set_callbacks(self, progress_callback, status_callback):
        """Set callbacks for progress and status updates"""
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def _update_progress(self, value: int):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(value)
    
    def _update_status(self, message: str):
        """Update status if callback is set"""
        if self.status_callback:
            self.status_callback(message)
    
    def get_files_in_folder(self, folder_path: str) -> List[str]:
        """Get list of all files in a folder (recursively)"""
        files = []
        if os.path.exists(folder_path):
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        return files
    
    def encrypt_file(self, file_path: str, output_dir: str, keys: Dict) -> Dict:
        """Encrypt a single file and save it to output directory"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Encrypt the file content
            ciphertext, nonce, signature = self.hybrid_system.encrypt_and_sign(
                file_content, keys['private_key']
            )
            
            # Create output file structure
            relative_path = os.path.relpath(file_path)
            output_file_path = os.path.join(output_dir, relative_path + '.encrypted')
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            # Save encrypted file
            encrypted_data = {
                'ciphertext': ciphertext.hex(),
                'nonce': nonce.hex(),
                'signature': {
                    'mu': signature[0].hex(),
                    'z': signature[1].tolist()
                },
                'original_filename': os.path.basename(file_path),
                'encrypted_at': datetime.now().isoformat(),
                'file_size': len(file_content)
            }
            
            with open(output_file_path, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            # Save keys alongside encrypted file
            keys_file_path = output_file_path.replace('.encrypted', '.keys')
            with open(keys_file_path, 'w') as f:
                keys_data = {
                    'public_key': {
                        'seed': keys['public_key']['seed'].hex(),
                        't': keys['public_key']['t'].tolist()
                    },
                    'private_key': {
                        'seed': keys['private_key']['seed'].hex(),
                        's1': keys['private_key']['s1'].tolist(),
                        's2': keys['private_key']['s2'].tolist(),
                        't': keys['private_key']['t'].tolist()
                    }
                }
                json.dump(keys_data, f, indent=2)
            
            return {
                'status': 'success',
                'original_file': file_path,
                'encrypted_file': output_file_path,
                'keys_file': keys_file_path,
                'file_size': len(file_content)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'original_file': file_path,
                'error': str(e)
            }
    
    def decrypt_file(self, encrypted_file_path: str, output_dir: str) -> Dict:
        """Decrypt a single encrypted file"""
        try:
            # Load encrypted data
            with open(encrypted_file_path, 'r') as f:
                encrypted_data = json.load(f)
            
            # Load keys
            keys_file_path = encrypted_file_path.replace('.encrypted', '.keys')
            with open(keys_file_path, 'r') as f:
                keys_data = json.load(f)
            
            # Reconstruct binary data
            ciphertext = bytes.fromhex(encrypted_data['ciphertext'])
            nonce = bytes.fromhex(encrypted_data['nonce'])
            signature = (
                bytes.fromhex(encrypted_data['signature']['mu']),
                np.array(encrypted_data['signature']['z'], dtype=np.int32)
            )
            
            # Reconstruct public key
            public_key = {
                'seed': bytes.fromhex(keys_data['public_key']['seed']),
                't': np.array(keys_data['public_key']['t'], dtype=np.int32)
            }
            
            # Decrypt the file
            decrypted_content = self.hybrid_system.verify_and_decrypt(
                ciphertext, nonce, signature, public_key
            )
            
            # Save decrypted file
            original_filename = encrypted_data['original_filename']
            output_file_path = os.path.join(output_dir, original_filename)
            
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            with open(output_file_path, 'wb') as f:
                f.write(decrypted_content)
            
            return {
                'status': 'success',
                'encrypted_file': encrypted_file_path,
                'decrypted_file': output_file_path,
                'original_filename': original_filename
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'encrypted_file': encrypted_file_path,
                'error': str(e)
            }
    
    def encrypt_folder(self, input_folder: str, output_folder: str, auto_generate_keys: bool = True) -> Dict:
        """Encrypt entire folder with automatic key generation"""
        try:
            self._update_status("Starting folder encryption...")
            
            # Get all files in the folder
            files = self.get_files_in_folder(input_folder)
            total_files = len(files)
            
            if total_files == 0:
                return {
                    'status': 'error',
                    'error': 'No files found in the specified folder'
                }
            
            self._update_status(f"Found {total_files} files to encrypt")
            
            # Generate keys if auto mode is enabled
            if auto_generate_keys:
                self._update_status("Generating encryption keys...")
                public_key, private_key = self.hybrid_system.generate_keys()
                keys = {'public_key': public_key, 'private_key': private_key}
            else:
                # Use existing keys (would need to be passed as parameter)
                raise ValueError("Manual key mode not yet implemented")
            
            # Create output folder
            os.makedirs(output_folder, exist_ok=True)
            
            # Encrypt each file
            results = []
            for i, file_path in enumerate(files):
                self._update_status(f"Encrypting file {i+1}/{total_files}: {os.path.basename(file_path)}")
                
                result = self.encrypt_file(file_path, output_folder, keys)
                results.append(result)
                
                # Update progress
                progress = int((i + 1) / total_files * 100)
                self._update_progress(progress)
                
                # Small delay to allow UI updates
                time.sleep(0.1)
            
            # Generate summary
            successful = sum(1 for r in results if r['status'] == 'success')
            failed = total_files - successful
            
            # Save encryption summary
            summary = {
                'encryption_completed_at': datetime.now().isoformat(),
                'input_folder': input_folder,
                'output_folder': output_folder,
                'total_files': total_files,
                'successful_encryptions': successful,
                'failed_encryptions': failed,
                'auto_generated_keys': auto_generate_keys,
                'results': results
            }
            
            summary_path = os.path.join(output_folder, 'encryption_summary.json')
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self._update_status(f"Encryption complete: {successful}/{total_files} files encrypted successfully")
            
            return {
                'status': 'success',
                'total_files': total_files,
                'successful': successful,
                'failed': failed,
                'summary_file': summary_path,
                'results': results
            }
            
        except Exception as e:
            self._update_status(f"Encryption failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def decrypt_folder(self, encrypted_folder: str, output_folder: str) -> Dict:
        """Decrypt entire folder of encrypted files"""
        try:
            self._update_status("Starting folder decryption...")
            
            # Find all encrypted files
            encrypted_files = []
            for root, dirs, filenames in os.walk(encrypted_folder):
                for filename in filenames:
                    if filename.endswith('.encrypted'):
                        encrypted_files.append(os.path.join(root, filename))
            
            total_files = len(encrypted_files)
            
            if total_files == 0:
                return {
                    'status': 'error',
                    'error': 'No encrypted files found in the specified folder'
                }
            
            self._update_status(f"Found {total_files} encrypted files to decrypt")
            
            # Create output folder
            os.makedirs(output_folder, exist_ok=True)
            
            # Decrypt each file
            results = []
            for i, encrypted_file_path in enumerate(encrypted_files):
                self._update_status(f"Decrypting file {i+1}/{total_files}: {os.path.basename(encrypted_file_path)}")
                
                result = self.decrypt_file(encrypted_file_path, output_folder)
                results.append(result)
                
                # Update progress
                progress = int((i + 1) / total_files * 100)
                self._update_progress(progress)
                
                # Small delay to allow UI updates
                time.sleep(0.1)
            
            # Generate summary
            successful = sum(1 for r in results if r['status'] == 'success')
            failed = total_files - successful
            
            self._update_status(f"Decryption complete: {successful}/{total_files} files decrypted successfully")
            
            return {
                'status': 'success',
                'total_files': total_files,
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            self._update_status(f"Decryption failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            } 