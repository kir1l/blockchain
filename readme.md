# BitPlace Chain & BitPlace Wallet

## Introduction

BitPlace Chain is a blockchain implementation with an integrated wallet system. This project demonstrates the fundamental concepts of blockchain technology and provides a simple wallet application for interacting with the blockchain.

## Project Structure

The project is organized into the following main components:

- `blockchain.py`: Core blockchain implementation
- `wallet/`: Wallet application
- `managers/`: Additional management modules
- `api.py`: API for interacting with the blockchain
- `main.py`: Entry point for running the application
- `logger.py`: Logging functionality

## Blockchain (blockchain.py)

The blockchain component implements the core functionality of the BitPlace Chain, including:

- Block creation and validation
- Chain management
- Consensus mechanisms
- Transaction handling

## Wallet Application (wallet/)

The wallet application provides user-friendly interfaces for:

- Creating and managing wallets
- Sending and receiving transactions
- Viewing transaction history
- Checking account balances

## Component Interaction

The various components of the BitPlace Chain project interact as follows:

1. The blockchain core (`blockchain.py`) maintains the chain and processes transactions.
2. The wallet application interacts with the blockchain through the API (`api.py`).
3. Managers in the `managers/` directory handle specific aspects of the system, such as node communication or data persistence.
4. The main application (`main.py`) initializes and coordinates the different components.

## Run Blockchain

1. Clone the repository:
```bash
git clone https://github.com/kir1l/blockchain.git
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the main application:
```bash
python main.py
```

## Run Wallet

1. Go to wallet folder:
```bash
cd wallet/
```

2. Run main wallet application:
```bash
python main.py
```

## Contributing

Contributions to the BitPlace Chain project are welcome. Please feel free to submit issues, fork the repository and send pull requests!

## License

MIT


