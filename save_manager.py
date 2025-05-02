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
            os.makedirs(self.saves_dir)
    
    def _generate_key(self, password: str) -> None:
        """Generate encryption key from password"""
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
        try:
            # Generate encryption key
            self._generate_key(password)
            
            # Convert game state to JSON
            json_data = json.dumps(game_state)
            
            # Encrypt the data
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            # Save to file
            save_path = os.path.join(self.saves_dir, f"{save_name}.sav")
            with open(save_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error saving game: {str(e)}")
            return False
    
    def load_game(self, save_name: str, password: str) -> dict:
        """
        Load game state from encrypted file
        
        Args:
            save_name: Name of the save file
            password: Password for decryption
            
        Returns:
            dict: Game state if successful, None if failed
        """
        try:
            # Generate encryption key
            self._generate_key(password)
            
            # Read encrypted file
            save_path = os.path.join(self.saves_dir, f"{save_name}.sav")
            with open(save_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Convert back to dictionary
            game_state = json.loads(decrypted_data.decode())
            
            return game_state
        except Exception as e:
            print(f"Error loading game: {str(e)}")
            return None
    
    def list_saves(self) -> list:
        """List all available save files"""
        saves = []
        for file in os.listdir(self.saves_dir):
            if file.endswith('.sav'):
                saves.append(file[:-4])  # Remove .sav extension
        return saves
    
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
            return False
        except Exception as e:
            print(f"Error deleting save: {str(e)}")
            return False 