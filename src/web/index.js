import React from 'react'
import { render } from 'react-dom'
import './index.scss'
import 'babel-polyfill'
import web3Init from './web3init'
import Contract from './Contract'

const DOMAIN = 'localhost'
const PORT = '8000'
const URL = `http://${DOMAIN}:${PORT}`

// const web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:7545'));

class App extends React.Component {
    constructor() {
        super()
        this.state = {
            message: 'first message'
        }
    }

    async displayServerMessage() {
        let message
        try {
            const response = await fetch(URL)
            const body = await response.json()
            message = body.status
        } catch (err) {
            message = err.message
        }

        this.setState({ message })
    }

    async getContracts() {
        let message

        try {
            const response = await fetch(`${URL}/contracts`)
            const body = await response.json()
            message = body
        } catch (err) {
            message = err.message
            alert(message)
            return
        }

        this.contract = new Contract(message)
    }

    componentDidMount() {
        this.displayServerMessage()

        setTimeout(()=> {
            this.setState({message: 'second message'})
        }, 5000)

        this.getContracts()
    }

    render() {
        return (
            <div>
                <h1>Etherpay payment system</h1>
            </div>
        )
    }
}

(async function startItUp() {
    const { validProvider, networkType } = await web3Init(window)
    console.log(validProvider, networkType)

    render(<App />, document.getElementById('root'));
})()

