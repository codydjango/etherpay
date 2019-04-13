pragma solidity ^0.5.0;

import 'openzeppelin-solidity/contracts/ownership/Ownable.sol';

contract Etherpay is Ownable {
    mapping(uint256 => Invoice) public invoices;

    uint256 private _balance;

    struct Invoice {
        bool paid;
        address from;
    }

    function getInvoice(uint256 orderId) public view returns (uint256, bool, address) {
        Invoice memory invoice = invoices[orderId];

        return (orderId, invoice.paid, invoice.from);
    }

    function pay(uint256 orderId) public payable returns (bool) {
        Invoice memory invoice = invoices[orderId];
        require(invoice.paid == false);

        // what happens if the payment is not enough?
        // the backend will validate it, and if need be the organizer can issue a refund to the sender
        _balance += msg.value;
        invoice.paid = true;
        invoice.from = msg.sender;

        return true;
    }

    function getBalance() public view onlyOwner returns (uint) {
        return _balance;
    }

    function withdraw() public onlyOwner returns (bool) {
        msg.sender.transfer(_balance);
        _balance = 0;
        return true;
    }
}
