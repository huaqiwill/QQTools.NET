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
    public partial class MainForm: Form
    {
        public MainForm()
        {
            InitializeComponent();
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            new LoginDialog().ShowDialog();
            new AuthDialog().ShowDialog();
        }

        private void 字典库ToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void 官网ToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void 反馈ToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void 关于ToolStripMenuItem1_Click(object sender, EventArgs e)
        {

        }

        private void 检查更新ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            new UpdateDialog().ShowDialog();
        }
    }
}
