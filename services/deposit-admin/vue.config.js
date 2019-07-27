module.exports = {
  devServer: {
    disableHostCheck: true,
    public: 'http://localhost:8080/admin'
  },
  crossorigin: "",
  chainWebpack: config => {
    config.module.rules.delete('eslint');
  },
  publicPath: '/admin/'
}
