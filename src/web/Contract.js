class Contract {
    constructor(compiled) {
        this.instance = new window.web3.eth.Contract(this.getArray(compiled.Etherpay.abi), "0x35122239ed172a4537D382AC449A6941a94e5E51")

        console.log(this.instance)
        window.contract = this.instance
    }

    getArray(abi) {
        let abiArray = []

        for (let i in abi) {
            abiArray.push(abi[i])
        }

        return abiArray
    }
}

export default Contract
