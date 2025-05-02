import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SaveManager:
    def __init__(self):
        self.saves_dir = "saves"
        self.key = None
        self.fernet = None
        
        # Create saves directory if it doesn't exist
        if not os.path.exists(self.saves_dir):
            try:
                os.makedirs(self.saves_dir)
            except Exception as e:
                print(f"Error creating saves directory: {str(e)}")
                raise
    
    def _generate_key(self, password: str) -> None:
        """Generate encryption key from password"""
        try:
            # Convert password to bytes
            password = password.encode()
            
            # Generate salt
            salt = b'EldoriaSaveSystem'  # Fixed salt for consistency
            
            # Generate key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.key = key
            self.fernet = Fernet(key)
        except Exception as e:
            print(f"Error generating encryption key: {str(e)}")
            raise
    
    def save_game(self, game_state: dict, save_name: str, password: str) -> bool:
        """
        Save game state to encrypted file
        
        Args:
            game_state: Dictionary containing game state
            save_name: Name of the save file
            password: Password for encryption
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        file = None
        try:
            # Generate encryption key
            self._generate_key(password)
            
            # Convert game state to JSON
            json_data = json.dumps(game_state)
            
            # Encrypt the data
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            # Save to file
            save_path = os.path.join(self.saves_dir, f"{save_name}.sav")
            file = open(save_path, 'wb')
            file.write(encrypted_data)
            
            return True
        except json.JSONDecodeError:
            print("Error: Invalid game state format")
            return False
        except Exception as e:
            print(f"Error saving game: {str(e)}")
            return False
        finally:
            if file:
                file.close()
    
    def load_game(self, save_name: str, password: str) -> dict:
        """
        Load game state from encrypted file
        
        Args:
            save_name: Name of the save file
            password: Password for decryption
            
        Returns:
            dict: Game state if successful, None if failed
        """
        file = None
        try:
            # Generate encryption key
            self._generate_key(password)
            
            # Read encrypted file
            save_path = os.path.join(self.saves_dir, f"{save_name}.sav")
            if not os.path.exists(save_path):
                print(f"Error: Save file '{save_name}' not found")
                return None
                
            file = open(save_path, 'rb')
            encrypted_data = file.read()
            
            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Convert back to dictionary
            game_state = json.loads(decrypted_data.decode())
            
            return game_state
        except json.JSONDecodeError:
            print("Error: Invalid save file format")
            return None
        except Exception as e:
            print(f"Error loading game: {str(e)}")
            return None
        finally:
            if file:
                file.close()
    
    def list_saves(self) -> list:
        """List all available save files"""
        try:
            saves = []
            for file in os.listdir(self.saves_dir):
                if file.endswith('.sav'):
                    saves.append(file[:-4])  # Remove .sav extension
            return saves
        except Exception as e:
            print(f"Error listing saves: {str(e)}")
            return []
    
    def delete_save(self, save_name: str) -> bool:
        """
        Delete a save file
        
        Args:
            save_name: Name of the save file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            save_path = os.path.join(self.saves_dir, f"{save_name}.sav")
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            print(f"Error: Save file '{save_name}' not found")
            return False
        except Exception as e:
            print(f"Error deleting save: {str(e)}")
            return False 