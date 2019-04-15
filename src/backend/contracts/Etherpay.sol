pragma solidity ^0.5.0;

import './Ownable.sol';

contract Etherpay is Ownable {
    mapping(uint256 => Invoice) public invoices;

    uint256 private _balance;

    struct Invoice {
        bool paid;
        uint256 amount;
        address payable from;
        bool refund;
    }

    event Paid(uint256 indexed orderId, uint256 indexed value, address indexed sender);
    event Refunded(uint256 indexed orderId, uint256 indexed value, address indexed sender);

    function getInvoice(uint256 orderId) public view returns (uint256, bool, bool, address) {
        Invoice memory invoice = invoices[orderId];

        return (orderId, invoice.paid, invoice.refund, invoice.from);
    }

    function pay(uint256 orderId) public payable returns (bool) {
        Invoice memory invoice = invoices[orderId];
        require(invoice.paid == false);

        // what happens if the payment is not enough?
        // the backend will validate it, and if need be the organizer can
        // issue a refund to the sender
        _balance += msg.value;
        invoice.paid = true;
        invoice.from = msg.sender;

        emit Paid(orderId, msg.value, msg.sender);

        return true;
    }

    function refund(uint256 orderId) public payable onlyOwner returns (bool) {
        Invoice memory invoice = invoices[orderId];

        require(invoice.paid == true);
        require(invoice.refund == false);

        _balance -= invoice.amount;

        invoice.from.transfer(invoice.amount);
        invoice.refund = true;

        emit Refunded(orderId, invoice.amount, invoice.from);

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

    function destroy() public onlyOwner returns (bool) {
        selfdestruct(msg.sender);
    }
}
