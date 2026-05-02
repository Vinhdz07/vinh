const accounts = [
  {
    game: "Lien Quan",
    badge: "Best Seller",
    name: "Acc Chien Than Full Tuong",
    description: "So huu nhieu skin huu han, phu hieu cao cap va lich su giao dich an toan.",
    rank: "Chien Than",
    skins: "165 skin",
    server: "Server VN",
    price: "3.490.000d",
    oldPrice: "4.200.000d",
    visualLabel: "Top 1",
    visualTitle: "MYTHIC"
  },
  {
    game: "Valorant",
    badge: "Hot Deal",
    name: "Acc Full Skin Vandal + Knife",
    description: "Phu hop cho nguoi choi thich kho skin dep, rank cao va email sach de doi thong tin.",
    rank: "Ascendant",
    skins: "42 skin",
    server: "APAC",
    price: "2.790.000d",
    oldPrice: "3.300.000d",
    visualLabel: "Prime",
    visualTitle: "RADIANT"
  },
  {
    game: "Free Fire",
    badge: "Gia Tot",
    name: "Acc Full Bo Sungleam + Hanh Dong",
    description: "Tai khoan co nhieu vat pham hiem, phu kien su kien va the vo cuc da kich hoat.",
    rank: "Huyen Thoai",
    skins: "120 vat pham",
    server: "VN",
    price: "1.250.000d",
    oldPrice: "1.590.000d",
    visualLabel: "Flash",
    visualTitle: "LEGEND"
  },
  {
    game: "Genshin",
    badge: "VIP",
    name: "Acc AR60 Nhieu 5 Sao",
    description: "Co nhieu nhan vat meta, vu khi tran tinh va tai nguyen ton du de build doi hinh.",
    rank: "AR60",
    skins: "11 nhan vat 5 sao",
    server: "Asia",
    price: "4.990.000d",
    oldPrice: "5.700.000d",
    visualLabel: "Rare",
    visualTitle: "CELESTIA"
  },
  {
    game: "FC Online",
    badge: "Meta Team",
    name: "Acc Full Team Mua Giai Moi",
    description: "Dan cau thu ICONS, team color dep va luong BP lon cho nguoi choi nang cap tiep.",
    rank: "Sieu Sao",
    skins: "32 ICONS",
    server: "VN",
    price: "2.150.000d",
    oldPrice: "2.680.000d",
    visualLabel: "Squad",
    visualTitle: "ICONS"
  },
  {
    game: "LMHT",
    badge: "Limited",
    name: "Acc Kim Cuong Nhieu Trang Phuc",
    description: "Co nhieu skin toi thuong, khung vien rank dep va lich su xep hang on dinh.",
    rank: "Kim Cuong I",
    skins: "210 skin",
    server: "VN2",
    price: "1.890.000d",
    oldPrice: "2.300.000d",
    visualLabel: "Elite",
    visualTitle: "CHALLENGER"
  }
];

const grid = document.querySelector("#accountGrid");
const template = document.querySelector("#accountCardTemplate");
const filterButtons = document.querySelectorAll(".filter-chip");

function renderAccounts(activeFilter = "all") {
  grid.innerHTML = "";

  const filteredAccounts =
    activeFilter === "all"
      ? accounts
      : accounts.filter((account) => account.game === activeFilter);

  filteredAccounts.forEach((account) => {
    const fragment = template.content.cloneNode(true);

    fragment.querySelector(".account-game").textContent = account.game;
    fragment.querySelector(".account-badge").textContent = account.badge;
    fragment.querySelector(".account-name").textContent = account.name;
    fragment.querySelector(".account-description").textContent = account.description;
    fragment.querySelector(".spec-rank").textContent = account.rank;
    fragment.querySelector(".spec-skins").textContent = account.skins;
    fragment.querySelector(".spec-server").textContent = account.server;
    fragment.querySelector(".price-current").textContent = account.price;
    fragment.querySelector(".price-old").textContent = account.oldPrice;
    fragment.querySelector(".account-visual-label").textContent = account.visualLabel;
    fragment.querySelector(".account-visual-title").textContent = account.visualTitle;

    grid.appendChild(fragment);
  });
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((chip) => chip.classList.remove("active"));
    button.classList.add("active");
    renderAccounts(button.dataset.filter);
  });
});

renderAccounts();
