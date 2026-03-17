const STORAGE_KEY = 'mealRecords';

function getToday() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

Page({
  data: {
    name: '',
    date: getToday(),
    remark: '',
    timeSlotOptions: ['早餐', '午餐', '晚餐', '夜宵'],
    mealTypeOptions: ['普通餐', '素食餐', '清真餐', '其他'],
    timeSlotIndex: -1,
    mealTypeIndex: -1
  },

  onNameInput(e) {
    this.setData({ name: e.detail.value });
  },

  onDateChange(e) {
    this.setData({ date: e.detail.value });
  },

  onTimeSlotChange(e) {
    this.setData({ timeSlotIndex: Number(e.detail.value) });
  },

  onMealTypeChange(e) {
    this.setData({ mealTypeIndex: Number(e.detail.value) });
  },

  onRemarkInput(e) {
    this.setData({ remark: e.detail.value });
  },

  submitForm() {
    const { name, date, remark, timeSlotOptions, mealTypeOptions, timeSlotIndex, mealTypeIndex } = this.data;

    if (!name.trim()) {
      wx.showToast({ title: '请填写姓名', icon: 'none' });
      return;
    }
    if (timeSlotIndex < 0) {
      wx.showToast({ title: '请选择时间段', icon: 'none' });
      return;
    }
    if (mealTypeIndex < 0) {
      wx.showToast({ title: '请选择报餐类型', icon: 'none' });
      return;
    }

    const record = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
      name: name.trim(),
      date,
      timeSlot: timeSlotOptions[timeSlotIndex],
      mealType: mealTypeOptions[mealTypeIndex],
      remark: remark.trim(),
      createdAt: new Date().toISOString()
    };

    const existing = wx.getStorageSync(STORAGE_KEY) || [];
    existing.push(record);
    wx.setStorageSync(STORAGE_KEY, existing);

    wx.showToast({ title: '提交成功', icon: 'success' });
    this.setData({
      name: '',
      date: getToday(),
      remark: '',
      timeSlotIndex: -1,
      mealTypeIndex: -1
    });
  },

  goAdmin() {
    wx.navigateTo({ url: '/pages/admin/admin' });
  }
});
