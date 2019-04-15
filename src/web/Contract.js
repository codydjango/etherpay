class Contract {
    constructor(abi, address) {
        this.address = address
        this.abi = abi

        this.options = {
            defaultGasPrice: '2000000000'
        }

        this.instance = new window.web3.eth.Contract(this.abi, this.address, this.options)
    }

    pay(orderId) {
        return this.contract.instance.methods.pay(orderId)
    }
}

export default Contract
