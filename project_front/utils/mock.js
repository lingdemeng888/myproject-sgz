function genCode(){
  return String(Math.floor(100000 + Math.random()*900000));
}
function maskPhone(p){
  return p && p.length>=7 ? p.slice(0,3)+'****'+p.slice(-4): p;
}
module.exports={ genCode, maskPhone };
