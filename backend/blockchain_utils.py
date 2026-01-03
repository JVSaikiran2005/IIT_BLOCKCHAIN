"""
Blockchain utility functions using eth-abi and requests
For interacting with smart contracts without web3.py
"""

import requests
from eth_abi import encode, decode
from typing import Optional, Dict, Any
import json


class BlockchainClient:
    """Client for interacting with blockchain via JSON-RPC"""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.request_id = 0
    
    def _make_request(self, method: str, params: list) -> Dict[str, Any]:
        """Make a JSON-RPC request"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        self.request_id += 1
        
        response = requests.post(self.rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            raise Exception(f"RPC Error: {result['error']}")
        
        return result.get("result")
    
    def call_contract(self, contract_address: str, data: str, block: str = "latest") -> Optional[str]:
        """Call a contract method (read-only)"""
        params = [{
            "to": contract_address,
            "data": data
        }, block]
        
        return self._make_request("eth_call", params)
    
    def get_balance(self, address: str, block: str = "latest") -> int:
        """Get balance of an address"""
        result = self._make_request("eth_getBalance", [address, block])
        return int(result, 16) if result else 0
    
    def encode_function_call(self, function_signature: str, *args) -> str:
        """Encode function call data"""
        # This is a simplified version - in production, use proper ABI encoding
        # For now, return placeholder
        return "0x" + "0" * 64
    
    def decode_function_result(self, types: list, data: str) -> tuple:
        """Decode function result"""
        if not data or data == "0x":
            return tuple()
        
        # Remove 0x prefix and convert to bytes
        data_bytes = bytes.fromhex(data[2:])
        return decode(types, data_bytes)


def encode_address(address: str) -> bytes:
    """Encode an Ethereum address"""
    # Remove 0x prefix if present
    if address.startswith("0x"):
        address = address[2:]
    return bytes.fromhex(address)


def validate_address(address: str) -> bool:
    """Validate Ethereum address format"""
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


