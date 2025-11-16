const { genCode, maskPhone } = require('../../../utils/mock');

Page({
  data:{ id:'', pwd:'', code:'', sentCode:'', canSend:false },
  onChangeId(e){ this.setData({ id:e.detail.value, canSend: !!e.detail.value }); },
  onChangePwd(e){ this.setData({ pwd:e.detail.value }); },
  onChangeCode(e){ this.setData({ code:e.detail.value }); },
  sendCode(){
    if(!this.data.id){ return wx.showToast({ title:'先填写学号/手机号', icon:'none' }); }
    const sent = genCode();
    this.setData({ sentCode: sent });
    wx.showToast({ title:`验证码已发送到 ${maskPhone(this.data.id)}`, icon:'none' });
  },
  login(){
    if(!this.data.id||!this.data.pwd){ return wx.showToast({ title:'请先完善账号与密码', icon:'none' }); }
    if(this.data.code!==this.data.sentCode){ return wx.showToast({ title:'验证码不正确', icon:'none' }); }
    wx.showToast({ title:'登录成功（示例）', icon:'success' });
  },
  toRegister(){ wx.navigateTo({ url: '/pages/student/register/index' }); }
});
