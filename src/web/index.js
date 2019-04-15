import React from 'react'
import { render } from 'react-dom'
import './index.scss'
import 'babel-polyfill'
import web3Init from './web3init'
import Contract from './Contract'

const DOMAIN = 'localhost'
const PORT = '8080'
const URL = `http://${DOMAIN}:${PORT}`


const Order = props => {
    console.log('order', props)
    return (<formset>
        <h3>Order number: { props.id }</h3>
        <h4>Total: ${ `${ props.amount } ${ props.currency }` }</h4>
    </formset>)
}

const Transaction = props => {
    console.log('transaction', props)
    const url = `https://etherscan.io/tx/${ props.transactionHash }`

    return (<formset>
        <p>Success! Your transaction has been broadcast and is going through the process of network confirmation.</p>
        <small>Please wait while your transaction is being confirmed.</small><br />
        <small>View the transaction on <a target="_blank" href={ url }>Etherscan.</a></small>
    </formset>)
}

const Conversion = props => {
    return (<formset>
        <p>
            <strong>Total: { props.amountInEther } ETH</strong><br />
            <small>Current price of Ether: { props.etherPrice }</small><br />
            <small>Source: <a href="https://coinmarketcap.com/">https://coinmarketcap.com/</a></small>
        </p>
    </formset>)
}

class App extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            order: { id: 3, amount: '80.00', currency: 'CAD' },
            transaction: null,
            conversion: null
        }

        this.pay = this.pay.bind(this)
        this.convert = this.convert.bind(this)
    }

    componentDidMount() {
        this.getContract()
    }

    async pay() {
        let response, body, accounts, defaultAccount

        try {
            accounts = await web3.eth.getAccounts()
            defaultAccount = (accounts && accounts.length > 0) ? accounts[0] : null
        } catch (err) {
            console.log('err', err)
            defaultAccount = null
        }

        if (!defaultAccount) {
            alert('no MetaMask account found. Please install MetaMask and try again.')
        }

        response = await fetch(`${ URL }/convert?amount=${ this.state.order.amount }&currency=${ this.state.order.currency }`)
        body = await response.json()

        const orderId = this.state.order.id
        const { amountInEther, conversionRate, etherPrice } = body.payload
        const account = defaultAccount
        const value = web3.utils.toWei(amountInEther.toString())
        const transaction = await this.contract.pay(orderId).send({ from: account, value: value })

        this.setState(state => {
            state.conversion = { amountInEther, conversionRate, etherPrice }
            state.transaction = transaction

            return state
        })
    }

    async convert() {
        const response = await fetch(`${ URL }/convert?amount=${ this.state.order.amount }&currency=${ this.state.order.currency }`)
        const body = await response.json()
        const { amountInEther, conversionRate, etherPrice } = body.payload

        this.setState(state => {
            state.conversion = { amountInEther, conversionRate, etherPrice }
            return state
        })
    }

    async getContract() {
        try {
            const response = await fetch(`${URL}/contract`)
            const json = await response.json()
            const { abi, address } = json.payload

            this.contract = new Contract(abi, address)
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <h1>Etherpay payment system</h1>

                { (this.state.order && (<Order { ...this.state.order } />)) }
                { (this.state.conversion && (<Conversion { ...this.state.conversion } />)) }
                { (this.state.transaction && (<Transaction { ...this.state.transaction } />)) }

                { (this.state.transaction == null) && (
                <div>
                    <button onClick={ this.convert }>Convert to Ether</button>
                    <button onClick={ this.pay }>Pay with MetaMask</button>
                </div>
                ) }

            </div>
        )
    }
}

(async function startItUp() {
    const { validProvider, networkType } = await web3Init(window)
    console.log(validProvider, networkType)

    render(<App />, document.getElementById('root'));
})()

