import Web3 from 'web3'

function getProviderType(provider) {
    if (provider.isMetaMask) return 'metamask'
    if (provider.isTrust) return 'trust'
    if (provider.isGoWallet) return 'goWallet'
    if (provider.isAlphaWallet) return 'alphaWallet'
    if (provider.isStatus) return 'status'
    if (provider.isToshi) return 'coinbase'
    if (typeof window.__CIPHER__ !== 'undefined') return 'cipher'
    if (provider.host && provider.host.indexOf('infura') !== -1) return 'infura'
    if (provider.host && provider.host.indexOf('localhost') !== -1) return 'localhost'
    if (window.ethereum && window.ethereum.isMetaMask) return 'metamask'

    return 'unknown'
}

export default async function web3Init() {
    let provider, web3, defaultAccount, providerType, isConnected, networkType, accounts, validProvider = false

    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
        provider = window.web3.currentProvider
        web3 = new Web3(provider)
        provider = web3.currentProvider
    }

    const web3Version = web3.version.api || web3.version
    isConnected = provider.connected || provider.isConnected

    console.log('web3version', web3Version)

    try {
        networkType = await web3.eth.net.getNetworkType()
    } catch (err) {
        networkType = 'unknown'
    }

    if (window.ethereum) {
        await window.ethereum.enable()
    }

    try {
        accounts = await web3.eth.getAccounts()
    } catch (err) {
    }

    if (accounts && accounts.length > 0) {
        defaultAccount = accounts[0]
    } else {
        defaultAccount = null
    }

    if (defaultAccount) validProvider = true

    window.web3 = web3

    return {
        web3,
        web3Version,
        providerType,
        isConnected,
        networkType,
        defaultAccount,
        validProvider
    }
}
