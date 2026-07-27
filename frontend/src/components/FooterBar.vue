<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-main">
        <div class="footer-brand">
          <div class="footer-logo">
            <img src="/images/logo.jpg" alt="华丽电器" class="footer-logo-img">
            <div>
              <strong>华丽电器制造有限公司</strong>
              <small>HUALI ELECTRIC MANUFACTURING CO., LTD</small>
            </div>
          </div>
          <p class="footer-desc">
            国家高新技术企业，浙江省专精特新中小企业。20年专注电动工具研发制造，产品远销80+国家和地区。
          </p>
        </div>
        <div class="footer-links">
          <h4>快速导航</h4>
          <router-link to="/about/">关于我们</router-link>
          <router-link to="/products/">产品中心</router-link>
          <router-link to="/news/">新闻中心</router-link>
          <router-link to="/contact/">联系我们</router-link>
        </div>
        <div class="footer-links">
          <h4>服务支持</h4>
          <router-link to="/inquiry/">在线询盘</router-link>
          <router-link to="/dealer/">经销商入口</router-link>
          <router-link to="/supply-chain/">供应链合作</router-link>
          <router-link to="/contact/">售后服务</router-link>
        </div>
        <div class="footer-contact">
          <h4>联系方式</h4>
          <p>📍 浙江省金华市武义县泉溪镇王元工业区</p>
          <p>📞 0579-8770****</p>
          <p>✉️ k****@cnkainuo</p>
          <p>🕐 周一至周五 8:00 - 17:00</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 华丽电器制造有限公司 Huali Electric. All Rights Reserved.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--dark); color: var(--gray-400); padding: 60px 0 0;
  border-top: 4px solid var(--brand);
}
.footer-main {
  display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 40px;
  padding-bottom: 40px;
}
.footer-logo { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.footer-logo-img { height: 40px; width: auto; }
.footer-logo strong { display: block; font-size: 16px; color: var(--white); }
.footer-logo small { font-size: 10px; color: var(--gray-500); }
.footer-desc { font-size: 13px; line-height: 1.8; color: var(--gray-500); }
.footer-links h4, .footer-contact h4 {
  color: var(--white); font-size: 15px; margin-bottom: 16px; position: relative;
  padding-bottom: 10px;
}
.footer-links h4::after, .footer-contact h4::after {
  content: ''; position: absolute; bottom: 0; left: 0;
  width: 30px; height: 2px; background: var(--brand);
}
.footer-links a {
  display: block; color: var(--gray-500); font-size: 13px;
  padding: 5px 0; transition: color .3s;
}
.footer-links a:hover { color: var(--brand); padding-left: 4px; }
.footer-contact p {
  font-size: 13px; padding: 4px 0; color: var(--gray-500);
}
.footer-bottom {
  border-top: 1px solid rgba(255,255,255,.06);
  padding: 20px 0; text-align: center; font-size: 12px; color: var(--gray-600);
}
@media (max-width: 768px) {
  .footer-main { grid-template-columns: 1fr 1fr; gap: 30px; }
}
@media (max-width: 480px) {
  .footer-main { grid-template-columns: 1fr; }
}
</style>
