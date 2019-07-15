module.exports = {
  devServer: {
      disableHostCheck: true
  },
  chainWebpack: config => {
    config.module.rules.delete('eslint');
  },
  publicpath: '/admin/'
}