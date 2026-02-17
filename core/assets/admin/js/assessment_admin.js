const CRITERIA_LABELS = {
  seq: "Sequencial",
  random: "Aleatório",
  MI: "MI - Máxima Informação",
  MEPV: "MEPV - Mínima Variância Posterior Esperada",
  MLWI: "MLWI - Informação Ponderada de Máxima Verossimilhança",
  MPWI: "MPWI - Informação Ponderada Máxima Posterior",
  MEI: "MEI - Informação Esperada Máxima",
  KL: "KL - Divergência Kullback-Leibler ponto a ponto",
  KLn: "KLn - Kullback-Leibler ponto a ponto com um valor delta decrescente",
  IKLP: "IKLP - Critérios de Kullback-Leibler Baseados em Integração com peso de densidade a priori",
  IKL: "IKL - Critérios de Kullback-Leibler Baseados em Integração",
  IKLn: "IKLn - Versão ponderada com itens raiz-n",
  IKLPn: "IKLPn - Versão ponderada com itens raiz-n",
  Drule: "DRULE - Determinante Máximo da Matriz de Informação",
  Trule:
    "TRULE - Traço Máximo (potencialmente ponderado) da Matriz de Informação",
  Arule:
    "ARULE - Traço Mínimo (potencialmente ponderado) da Matriz de Covariância Assintótica",
  Erule: "ERULE - Valor Mínimo da Matriz de Informação",
  Wrule: "WRULE - Critérios de Informação Ponderada",
  DPrule: "DPRULE - Para Drule",
  TPrule: "TPRULE - Para Trule",
  APrule: "APRULE - Para Arule",
  EPrule: "EPRULE - Para Erule",
  WPrule: "WPRULE - Para Wrule",
  SHE: "SHE - Entropia Shennon da Habilidade do Sujeito",
  CDMKL: "KL - Divergência Kullback-Leibler",
  PWKL: "PWKL - Divergência Kullback-Leibler Ponderada",
  MPWKL: "MPWKL - Divergência Kullback-Leibler Ponderada de Máxima Posterior",
};

const get_criterias = (model) => {
  const IRT_MODELS = ["1PL", "2PL", "3PL", "4PL"];
  const MIRT_MODELS = ["M1PL", "M2PL", "M3PL", "M4PL"];
  const CDM_MODELS = ["DINA", "DINO", "GDINA"];

  const base_criterias = ["seq", "random"];

  if (IRT_MODELS.includes(model)) {
    return base_criterias.concat([
      "MI",
      "MEPV",
      "MLWI",
      "MPWI",
      "MEI",
      "KL",
      "KLn",
      "IKLP",
      "IKL",
      "IKLn",
      "IKLPn",
    ]);
  }

  if (MIRT_MODELS.includes(model)) {
    return base_criterias.concat([
      "KL",
      "KLn",
      "Drule",
      "Trule",
      "Arule",
      "Erule",
      "Wrule",
      "DPrule",
      "TPrule",
      "APrule",
      "EPrule",
      "WPrule",
    ]);
  }

  if (CDM_MODELS.includes(model)) {
    return base_criterias.concat(["SHE", "CDMKL", "PWKL", "MPWKL"]);
  }

  return base_criterias;
};

const populate_criteria_options = (model) => {
  const criterias = get_criterias(model);
  const criteria_select = document.getElementById("id_criteria");

  const previousValue = criteria_select.value;

  criteria_select.innerHTML = "";

  criterias.forEach((criteria) => {
    const option = document.createElement("option");
    option.value = criteria;
    option.text = CRITERIA_LABELS[criteria];
    criteria_select.appendChild(option);
  });

  criteria_select.value = criterias.includes(previousValue)
    ? previousValue
    : criterias[0];
};

const toggle_stop_fields = (model) => {
  const isCdmModel = ["DINA", "DINO", "GDINA"].includes(model);
  document.getElementsByClassName("field-delta_thetas")[0].style.display =
    isCdmModel ? "none" : "block";
  document.getElementsByClassName("field-min_sem")[0].style.display = isCdmModel
    ? "none"
    : "block";
  document.getElementsByClassName("field-threshold")[0].style.display =
    isCdmModel ? "block" : "none";
};

document.addEventListener("DOMContentLoaded", () => {
  const type_select = document.getElementById("id_type");
  type_select.addEventListener("change", (event) => {
    const selected_type = event.target.value;
    populate_criteria_options(selected_type);
    toggle_stop_fields(selected_type);
  });
  const initial_type = type_select.value;
  populate_criteria_options(initial_type);
  toggle_stop_fields(initial_type);
});
