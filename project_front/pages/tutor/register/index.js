const { genCode, maskPhone } = require('../../../utils/mock');

Page({
  data:{ no:'', name:'', dept:'', phone:'', code:'', sent:'', pwd1:'', pwd2:'', a:0, b:0, va:'',
    depts:['行政','机电工程系','信息工程系','电子工程系','服装工程系','艺术设计系','经济贸易系'] },
  onLoad(){ this.refreshQA(); },
  refreshQA(){ const a=Math.floor(10+Math.random()*90), b=Math.floor(10+Math.random()*90); this.setData({ a,b }); },
  onNo(e){ this.setData({ no:e.detail.value }); },
  onName(e){ this.setData({ name:e.detail.value }); },
  onDeptChange(e){ const i=Number(e.detail.value); this.setData({ dept:this.data.depts[i] }); },
  onPhone(e){ this.setData({ phone:e.detail.value }); },
  onCode(e){ this.setData({ code:e.detail.value }); },
  onPwd1(e){ this.setData({ pwd1:e.detail.value }); },
  onPwd2(e){ this.setData({ pwd2:e.detail.value }); },
  onVA(e){ this.setData({ va:e.detail.value }); },
  sendCode(){ if(!this.data.phone) return wx.showToast({ title:'请输入手机号', icon:'none' }); const c=genCode(); this.setData({ sent:c }); wx.showToast({ title:`验证码已发送到 ${maskPhone(this.data.phone)}`, icon:'none' }); },
  submit(){
    const {no,name,dept,phone,code,sent,pwd1,pwd2,a,b,va}=this.data;
    if(!(no&&name&&dept&&phone&&pwd1&&pwd2&&code)) return wx.showToast({ title:'请完善注册信息', icon:'none' });
    if(pwd1!==pwd2) return wx.showToast({ title:'两次密码不一致', icon:'none' });
    if(code!==sent) return wx.showToast({ title:'验证码错误', icon:'none' });
    if(Number(va)!==a+b) return wx.showToast({ title:'安全验证未通过', icon:'none' });
    wx.showModal({ title:'注册结果', content:'恭喜您注册成功（示例）', showCancel:false });
  },
  backToLogin(){ wx.navigateBack(); }
});
