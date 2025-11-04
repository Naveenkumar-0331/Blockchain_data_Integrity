import hashlib
import time
import json
from datetime import datetime


def hash_student_record(name, roll_no, gpa):
    record_string = f"{name}_{roll_no}_{gpa}"
    return hashlib.sha256(record_string.encode()).hexdigest()


class Block:
    def __init__(self,index,timestamp,data,previous_hash):
        self.index=index
        self.timestamp=timestamp
        self.data=data
        self.previous_hash=previous_hash
        self.hash=self.calculate_hash()

    def calculate_hash(self):
        block_string=f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain=[self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0,time.time(),"Genesis Block","0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self,new_data):
        prev_block=self.get_latest_block()
        new_block=Block(len(self.chain),time.time(),new_data,prev_block.hash) 
        self.chain.append(new_block)

    def is_chain_valid(self):
    # loop through all blocks (except genesis block)
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # 1️⃣ Check if the hash is still correct
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Block {i} hash has been changed!")
                return False

            # 2️⃣ Check if current block points to correct previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block {i}'s previous hash doesn't match Block {i-1}'s hash!")
                return False

        print("✅ Blockchain is valid and untampered.")
        return True
    

    def verify_student_record(self, name, roll_no, gpa):
        # Step 1: re-create the same hash from user input
        record_hash = hashlib.sha256(f"{name}_{roll_no}_{gpa}".encode()).hexdigest()

        # Step 2: search for this hash in all blocks
        for block in self.chain:
            if block.data == record_hash:
                print(f"✅ Record found in block {block.index}")
                print(f"Timestamp: {block.timestamp}")
                return True

        print("❌ Record not found or may have been tampered.")
        return False
    

    def save_chain(self, filename="blockchain_data.json"):
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "previous_hash": block.previous_hash,
                "hash": block.hash
            })
        with open(filename, "w") as f:
            json.dump(chain_data, f, indent=4)
        print(f"💾 Blockchain saved to {filename}")

    def load_chain(self, filename="blockchain_data.json"):
        try:
            with open(filename, "r") as f:
                chain_data = json.load(f)
            self.chain = []
            for block_dict in chain_data:
                block = Block(
                    block_dict["index"],
                    block_dict["timestamp"],
                    block_dict["data"],
                    block_dict["previous_hash"]
                )
                # Manually set the hash (so it matches the saved one)
                block.hash = block_dict["hash"]
                self.chain.append(block)
            print(f"📂 Blockchain loaded from {filename}")
        except FileNotFoundError:
            print("⚠️ No previous blockchain file found. Creating a new one.")
            self.chain = [self.create_genesis_block()]


if __name__ == "__main__":
    print("="*60)
    print("🔗  BLOCKCHAIN-BASED ACADEMIC RECORD SYSTEM")
    print("="*60)

    edu_chain = Blockchain()    
    edu_chain.load_chain()
    
    print("=== Academic Record Blockchain ===")
    while True:
        print("\n1. Add new student record")
        print("2. View all blocks")
        print("3. Verify blockchain integrity")
        print("4. Verify student record")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter student name: ")
            roll = input("Enter roll number: ")
            gpa = input("Enter GPA: ")

            record_hash = hash_student_record(name, roll, gpa)
            edu_chain.add_block(record_hash)
            print("✅ Record added successfully!")

        elif choice == "2":
            for block in edu_chain.chain:
                timestamp_str = datetime.fromtimestamp(block.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                print(f"\nIndex: {block.index}")
                print(f"Timestamp: {timestamp_str}")
                print(f"Data (record hash): {block.data}")
                print(f"Hash: {block.hash}")
                print(f"Prev Hash: {block.previous_hash}")

        elif choice == "3":
            edu_chain.is_chain_valid()

        elif choice == "4":
            name = input("Enter student name: ")
            roll = input("Enter roll number: ")
            gpa = input("Enter GPA: ")
            edu_chain.verify_student_record(name, roll, gpa)


        elif choice == "5":
            edu_chain.save_chain()
            print("Exiting... Blockchain saved successfully.")
            break

        else:
            print("Invalid choice, try again.")
