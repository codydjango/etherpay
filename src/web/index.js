import React from 'react'
import { render } from 'react-dom'
import './index.scss'
import 'babel-polyfill'
import web3Init from './web3init'
import Contract from './Contract'


const DOMAIN = 'localhost'
const PORT = '8080'
const URL = `http://${DOMAIN}:${PORT}`
const EURO = '€'
const DOLLAR = '$'

function getSymbol(currency) {
    return (currency === 'EUR') ? EURO : DOLLAR
}

const Order = props => {
    const symbol = getSymbol(props.currency)

    return (<fieldset style={{ marginBottom: '1em' }}>
        <legend>Order #{ props.id }</legend>
        <p><strong>Total: { `${ symbol }${ props.amount } ${ props.currency }` }</strong></p>
    </fieldset>)
}

const Status = props => {
    let status, text, url, eth, blockNumber

    if (props.transaction) {
        status = 'Broadcast'
        text = 'Transaction broadcast, awaiting confirmation.'
        url = `https://etherscan.io/tx/${ props.transaction.transactionHash }`
    }

    if (props.polling) {
        status = 'Waiting'
    }

    if (props.order.paid && props.order.wei) {
        status = 'Confirmed'
        text = 'Your payment has been accepted.'
        eth = window.web3.utils.fromWei(props.order.wei)
        blockNumber = props.order.blockNumber
    }

    return (<fieldset style={{ marginBottom: '1em' }}>
        <legend>Status: { status }</legend>
        <p><strong>{ text }</strong></p>

        { (eth) && (<small style={{ display: 'block' }}>Total paid : { eth } ETH</small>) }
        { (blockNumber) && (<small style={{ display: 'block' }}>Mined in block: { blockNumber }</small>) }
        { (url) && (<small style={{ display: 'block' }}>View the transaction on <a target="_blank" href={ url }>Etherscan.</a></small>) }
    </fieldset>)
}

const Conversion = props => {
    const symbol = getSymbol(props.currency)

    return (<fieldset style={{ marginBottom: '1em' }}>
        <legend>Conversion</legend>
        <p><strong>Total: { props.amountInEther } ETH</strong></p>

        <small style={{ display: 'block' }}>Current ETH price in { props.currency }: { symbol }{ props.etherPrice }</small>
        <small style={{ display: 'block' }}>Source: <a href="https://coinmarketcap.com/">https://coinmarketcap.com/</a></small>
    </fieldset>)
}

class App extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            order: null,
            transaction: null,
            conversion: null,
            payButtonDisabled: true,
            polling: false
        }

        this.pay = this.pay.bind(this)
        this.convert = this.convert.bind(this)
        this.startPolling = this.startPolling.bind(this)
        this.confirmOrder = this.confirmOrder.bind(this)
    }

    componentDidMount() {
        this.getContract()
        this.getOrder()
    }

    get resolved() {
        return (this.state.order && this.state.order.paid && this.state.order.paid === true)
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
        const { amountInEther, etherPrice } = body.payload
        const account = defaultAccount
        const value = web3.utils.toWei(amountInEther.toString())

        const transaction = await this.contract.pay(orderId).send({
            to: this.contract.address,
            from: account,
            value: value
        })

        this.startPolling()

        this.setState(state => {
            state.conversion = { amountInEther, etherPrice }
            state.transaction = transaction

            return state
        })
    }

    startPolling() {
        let response, body

        this.setState(state => {
            state.polling = true
            return state
        }, () => {
            this.poll = setInterval(async () => {
                try {
                    response = await fetch(`${ URL }/order/${ this.state.order.id }`)
                    body = await response.json()

                    if (body.status === 'success' && body.payload && body.payload.paid === true) {
                        this.stopPolling()
                        this.confirmOrder(body.payload)
                    }
                } catch (err) {
                    console.log('err', err)
                }
            }, 1000)
        })
    }

    stopPolling() {
        this.setState(state=> {
            state.polling = false
            return state
        }, () => {
            clearInterval(this.poll)
        })
    }

    confirmOrder(order) {
        this.setState(state => {
            state.order.blockNumber = order.block_number
            state.order.wei = order.wei
            state.order.paid = order.paid

            return state
        })
    }

    async convert() {
        const response = await fetch(`${ URL }/convert?amount=${ this.state.order.amount }&currency=${ this.state.order.currency }`)
        const body = await response.json()
        const { amountInEther, etherPrice } = body.payload

        this.setState(state => {
            state.conversion = { amountInEther, etherPrice }
            state.payButtonDisabled = false
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

    async getOrder() {
        try {
            const response = await fetch(`${URL}/order`)
            const json = await response.json()
            const { id, amount, currency } = json.payload

            this.setState(state => {
                state.order = { id, amount, currency }
                return state
            })
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <h1>EtherPay</h1>
                <h2><em>Pluggable Ethereum payment processor for order management systems.</em></h2>
                <p>Proof of concept built with:</p>
                <ul>
                    <li>React 16.7.0</li>
                    <li>MetaMask 1.0.0-beta.46</li>
                    <li>Python 3.6/Flask 1.0.2/PyWeb3 4.9.1</li>
                    <li>Solidity 0.5/Remix</li>
                </ul>
                <hr />

                { (this.state.order && (<Order { ...this.state.order } />)) }
                { (this.state.conversion && (<Conversion currency={ this.state.order.currency } { ...this.state.conversion } />)) }
                { (this.state.polling || this.resolved) && (<Status {  ...this.state } />) }
                { (this.state.transaction === null) && (
                <fieldset style={{ marginBottom: '1em' }}>
                    <legend>Actions</legend>
                    <button onClick={ this.convert }>Convert to Ether</button>
                    <button disabled={ this.state.payButtonDisabled } onClick={ this.pay }>Pay with MetaMask</button>
                </fieldset>
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

