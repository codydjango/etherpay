import web3 from 'web3'
import React from 'react'
import { render } from 'react-dom'
import './index.scss'

class App extends React.Component {
  render() {
    return (
        <div>
            <h1>Eth payment system</h1>
        </div>
    )
  }
}

(function startItUp() {
    render(<App />, document.getElementById('root'));
})()

