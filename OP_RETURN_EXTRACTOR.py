import json
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import traceback

def get_op_return_data(txid, rpc_connection):
    try:
        print(f"Retrieving transaction: {txid}")
        raw_tx = rpc_connection.getrawtransaction(txid, 1)
        for vout in raw_tx['vout']:
            if 'scriptPubKey' in vout and 'asm' in vout['scriptPubKey']:
                asm = vout['scriptPubKey']['asm']
                if 'OP_RETURN' in asm:
                    hex_data = asm.split('OP_RETURN ')[1]
                    try:
                        decoded_data = bytes.fromhex(hex_data).decode('utf-8')
                        return decoded_data
                    except ValueError:
                        return f"Hex data: {hex_data} (Decoding failed)"
        print(f"OP_RETURN data not found for transaction: {txid}")
        return None
    except JSONRPCException as e:
        print(f"Error retrieving data for {txid}: {e}")
        print(f"RPC Error details: {e.error}")
        return None
    except Exception as e:
        print(f"Unexpected error retrieving data for {txid}: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def process_transaction_ids(json_file, rpc_user, rpc_password, rpc_host='127.0.0.1', rpc_port=14122, output_file="op_return_data.txt"): #change output file to .txt
    try:
        rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")
        print(f"Successfully connected to RPC: {rpc_host}:{rpc_port}")
    except Exception as e:
        print(f"Error connecting to RPC: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        input("Press Enter to exit...")
        return

    try:
        with open(json_file, 'r') as f:
            transaction_data = json.load(f)
        print(f"Successfully loaded transaction IDs from: {json_file}")
    except FileNotFoundError:
        print(f"Error: Transaction ID file not found at: {json_file}")
        input("Press Enter to exit...")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in: {json_file}")
        input("Press Enter to exit...")
        return
    except Exception as e:
        print(f"Unexpected error loading JSON file: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        input("Press Enter to exit...")
        return

    op_return_values = [] #create a list to hold the values.
    for txid in transaction_data['txids']:
        op_return_data = get_op_return_data(txid, rpc_connection)
        if op_return_data:
            op_return_values.append(op_return_data) #append the value to the list.

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile: #open as a text file.
            for value in op_return_values:
                outfile.write(value + "\n") #write each value on a new line.
        print(f"OP_RETURN data written to: {output_file}")
    except Exception as e:
        print(f"Error writing OP_RETURN data to file: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        input("Press Enter to exit...")
        return

    input("Script completed. Press Enter to exit...")

# Example usage
rpc_user = "username here"
rpc_password = "pw here"
json_file_path = r"your file path of the transactions file e.g., C:\Users\Me\Desktop\Declaration_of_Independence.json"
rpc_host = '127.0.0.1' #This is default mine was default there is a value above too in def process_transaction_ids
rpc_port = 14122 #port number here default is 14022 mine was 14122 there is a value above too in def process_transaction_ids

process_transaction_ids(json_file_path, rpc_user, rpc_password, rpc_host, rpc_port)