pragma solidity ^0.5.0;

import 'openzeppelin-solidity/contracts/ownership/Ownable.sol';

contract Payments is Ownable {
    mapping(uint256 => Invoice) public invoices;
    mapping(uint256 => Receipt) public receipts;

    uint256 private _balance;

    struct Invoice {
        uint256 orderId;
        uint256 amount;
        bool paid;
    }

    struct Receipt {
        uint256 orderId;
        uint256 amount;
        address paymentFrom;
        uint256 timestampPaid;
    }

    function createInvoice(uint256 orderId, uint256 amount) public onlyOwner {
        invoices[orderId] = Invoice(orderId, amount, false);
    }

    function getInvoice(uint256 orderId) public view returns (uint256, uint256, bool) {
        Invoice memory invoice = invoices[orderId];

        return (invoice.orderId, invoice.amount, invoice.paid);
    }

    function getReceipt(uint256 orderId) public view returns (uint256, uint256, address, uint256) {
        Receipt memory receipt = receipts[orderId];

        return (receipt.orderId, receipt.amount, receipt.paymentFrom, receipt.timestampPaid);
    }

    function pay(uint256 orderId) public payable returns (bool) {
        Invoice memory invoice = invoices[orderId];
        require(invoice.paid == false);


        _balance += msg.value;
        invoice.paid = true;

        // generate receipt
        receipts[orderId] = Receipt(orderId, invoice.amount, msg.sender, block.timestamp);

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
