const SETTINGS_KEY = 'mealAdminSettings';

function normalizeUsers(text) {
  return text
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((item, index, arr) => arr.indexOf(item) === index);
}

Page({
  data: {
    currentUser: '',
    adminUsersText: ''
  },

  onLoad() {
    const settings = wx.getStorageSync(SETTINGS_KEY) || {};
    const currentUser = settings.currentUser || '';
    const adminUsers = Array.isArray(settings.adminUsers) ? settings.adminUsers : [];

    this.setData({
      currentUser,
      adminUsersText: adminUsers.join('\n')
    });
  },

  onCurrentUserInput(e) {
    this.setData({ currentUser: e.detail.value });
  },

  onAdminUsersInput(e) {
    this.setData({ adminUsersText: e.detail.value });
  },

  saveSettings() {
    const currentUser = this.data.currentUser.trim();
    const adminUsers = normalizeUsers(this.data.adminUsersText);

    wx.setStorageSync(SETTINGS_KEY, {
      currentUser,
      adminUsers
    });

    wx.showToast({ title: '保存成功', icon: 'success' });
  },

  backToForm() {
    wx.navigateBack({
      fail: () => {
        wx.switchTab({
          url: '/pages/form/form',
          fail: () => wx.reLaunch({ url: '/pages/form/form' })
        });
      }
    });
  }
});
