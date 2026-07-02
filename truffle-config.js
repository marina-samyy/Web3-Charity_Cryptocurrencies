module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",     // عنوان Ganache
      port: 7545,            // البورت اللي في الصورة عندك
      network_id: "*",       // أي شبكة
    },
  },
  compilers: {
    solc: {
      version: "0.8.20", // رجعها لـ 0.8.20 عشان خاطر OpenZeppelin
      settings: {
        evmVersion: "paris" // دي أهم كلمة! بتلغي الـ PUSH0 اللي بيعمل الـ invalid opcode
      }
    }
  }
};