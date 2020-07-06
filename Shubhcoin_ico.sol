pragma solidity >=0.4.22 <0.7.0;

contract Shubhcoin_ico{
    
    //introducing max no of shubhcoins available for sales
    uint public max_shubhcoins = 1000000;
    
    //value of each usd in shubhcoin
    uint public usd_to_shubhcoins = 1000;
    
    //introducing total number of coins bought by invester
    uint public total_shubhcoins_bought = 0;
    
    //mapping investers address to its equity in shubhcoins and usd
    mapping(address => uint) equity_shubhcoins;
    mapping(address => uint) equity_usd;
    
    //checking if the investors can buy shubhcoins
    modifier can_buy_shubhcoins(uint usd_invested){
        require(usd_invested*usd_to_shubhcoins+total_shubhcoins_bought <= max_shubhcoins);
        _;
    }
    
    //getting the equity in shubhcoins of an investor
    function equity_in_shubhcoins(address investor) external constant returns(uint){
        return equity_shubhcoins[investor];
    }
    
    //getting the equity in usd of an investor
    function equity_in_usd(address investor) external constant returns(uint){
        return equity_usd[investor];
    }
    
    //buying shubhcoins
    function buy_shubhcoins(address investor,uint usd_invested) external
    can_buy_shubhcoins(usd_invested){
        uint shubhcoins_bought=usd_invested*usd_to_shubhcoins;
        equity_shubhcoins[investor] += shubhcoins_bought;
        equity_usd[investor] = equity_shubhcoins[investor]/1000;
        total_shubhcoins_bought+=shubhcoins_bought;
    }
    
    //selling shubhcoins
    function sell_shubhcoins(address investor,uint shubhcoins_sold) external{
        equity_shubhcoins[investor] -= shubhcoins_sold;
        equity_usd[investor] = equity_shubhcoins[investor]/1000;
        total_shubhcoins_bought-=shubhcoins_sold;
    }
    
}