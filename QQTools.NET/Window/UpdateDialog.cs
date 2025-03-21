using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace QQTools.NET.Window
{
    public partial class UpdateDialog: Form
    {
        public UpdateDialog()
        {
            InitializeComponent();
        }

        private void UpdateDialog_Load(object sender, EventArgs e)
        {
            var htmlContent = @"<div style=""width: 100%; max-width: 500px; padding: 20px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; font-family: Arial, sans-serif;"">
    <h2 style=""color: #333; text-align: center;"">✨ 新版本更新通知 ✨</h2>
    <p style=""color: #555; line-height: 1.6;"">
        亲爱的用户，感谢您的支持！我们已发布新的版本，为您带来更好的体验。以下是本次更新内容：
    </p>
    <ul style=""color: #555; padding-left: 20px;"">
        <li>🚀 性能优化，提高运行速度</li>
        <li>🐞 修复已知 Bug，提升稳定性</li>
        <li>🎨 界面优化，更美观易用</li>
        <li>🆕 新增功能，满足更多需求</li>
    </ul>
    <p style=""color: #555;"">
        立即更新，以体验最新功能！
    </p>
    <div style=""text-align: center; margin-top: 15px;"">
        <a href=""your_update_link_here"" style=""display: inline-block; padding: 10px 20px; background: #007bff; color: #fff; text-decoration: none; border-radius: 5px;"">立即更新</a>
    </div>
</div>
";
            webBrowser1.DocumentText = htmlContent;
        }

        private void webBrowser1_DocumentCompleted(object sender, WebBrowserDocumentCompletedEventArgs e)
        {

        }
    }
}
