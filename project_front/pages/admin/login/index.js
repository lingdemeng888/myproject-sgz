const { genCode, maskPhone } = require('../../../utils/mock');

Page({
  data:{ id:'215531241', pwd:'Admin@123', code:'', sentCode:'', canSend:true, phone:'15606136616' },
  onChangeId(e){ this.setData({ id:e.detail.value }); },
  onChangePwd(e){ this.setData({ pwd:e.detail.value }); },
  onChangeCode(e){ this.setData({ code:e.detail.value }); },
  sendCode(){
    const c = genCode();
    this.setData({ sentCode:c });
    wx.showToast({ title:`验证码已发送到 ${maskPhone(this.data.phone)}`, icon:'none' });
  },
  login(){
    if(this.data.code!==this.data.sentCode){ return wx.showToast({ title:'验证码不正确', icon:'none' }); }
    wx.showToast({ title:'登录成功（示例）', icon:'success' });
  }
});
