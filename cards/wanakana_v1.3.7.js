// WanaKana v1.3.7.
var wanakana, __indexOf = [].indexOf || function(a) {
  for (var b = 0, c = this.length; c > b; b++)
    if (b in this && this[b] === a) return b;
  return -1
};
wanakana = wanakana || {}, wanakana.version = "1.3.7", "function" == typeof define && define.amd && define("wanakana", [], function() {
  return wanakana
}), wanakana.LOWERCASE_START = 97, wanakana.LOWERCASE_END = 122, wanakana.UPPERCASE_START = 65, wanakana.UPPERCASE_END = 90, wanakana.HIRAGANA_START = 12353, wanakana.HIRAGANA_END = 12438, wanakana.KATAKANA_START = 12449, wanakana.KATAKANA_END = 12538, wanakana.LOWERCASE_FULLWIDTH_START = 65345, wanakana.LOWERCASE_FULLWIDTH_END = 65370, wanakana.UPPERCASE_FULLWIDTH_START = 65313, wanakana.UPPERCASE_FULLWIDTH_END = 65338, wanakana.defaultOptions = {
  useObseleteKana: !1,
  IMEMode: !1
}, wanakana.bind = function(a) {
  return a.addEventListener("input", wanakana._onInput)
}, wanakana.unbind = function(a) {
  return a.removeEventListener("input", wanakana._onInput)
}, wanakana._onInput = function(a) {
  var b, c, d, e, f, g;
  if (b = a.target, f = b.selectionStart, g = b.value.length, d = wanakana._convertFullwidthCharsToASCII(b.value), c = wanakana.toKana(d, {
      IMEMode: !0
    }), d !== c) {
    if (b.value = c, "number" == typeof b.selectionStart) return b.selectionStart = b.selectionEnd = b.value.length;
    if ("undefined" != typeof b.createTextRange) return b.focus(), e = b.createTextRange(), e.collapse(!1), e.select()
  }
}, wanakana._extend = function(a, b) {
  var c;
  if (null == a) return b;
  for (c in b) null == a[c] && null != b[c] && (a[c] = b[c]);
  return a
}, wanakana._isCharInRange = function(a, b, c) {
  var d;
  return d = a.charCodeAt(0), d >= b && c >= d
}, wanakana._isCharVowel = function(a, b) {
  var c;
  return null == b && (b = !0), c = b ? /[aeiouy]/ : /[aeiou]/, -1 !== a.toLowerCase().charAt(0).search(c)
}, wanakana._isCharConsonant = function(a, b) {
  var c;
  return null == b && (b = !0), c = b ? /[bcdfghjklmnpqrstvwxyz]/ : /[bcdfghjklmnpqrstvwxz]/, -1 !== a.toLowerCase().charAt(0).search(c)
}, wanakana._isCharKatakana = function(a) {
  return wanakana._isCharInRange(a, wanakana.KATAKANA_START, wanakana.KATAKANA_END)
}, wanakana._isCharHiragana = function(a) {
  return wanakana._isCharInRange(a, wanakana.HIRAGANA_START, wanakana.HIRAGANA_END)
}, wanakana._isCharKana = function(a) {
  return wanakana._isCharHiragana(a) || wanakana._isCharKatakana(a)
}, wanakana._isCharNotKana = function(a) {
  return !wanakana._isCharHiragana(a) && !wanakana._isCharKatakana(a)
}, wanakana._convertFullwidthCharsToASCII = function(a) {
  var b, c, d, e, f, g;
  for (c = a.split(""), e = f = 0, g = c.length; g > f; e = ++f) b = c[e], d = b.charCodeAt(0), wanakana._isCharInRange(b, wanakana.LOWERCASE_FULLWIDTH_START, wanakana.LOWERCASE_FULLWIDTH_END) && (c[e] = String.fromCharCode(d - wanakana.LOWERCASE_FULLWIDTH_START + wanakana.LOWERCASE_START)), wanakana._isCharInRange(b, wanakana.UPPERCASE_FULLWIDTH_START, wanakana.UPPERCASE_FULLWIDTH_END) && c[e](String.fromCharCode(d - wanakana.UPPERCASE_FULLWIDTH_START + wanakana.UPPERCASE_START));
  return c.join("")
}, wanakana._katakanaToHiragana = function(a) {
  var b, c, d, e, f, g, h;
  for (c = [], h = a.split(""), f = 0, g = h.length; g > f; f++) e = h[f], wanakana._isCharKatakana(e) ? (b = e.charCodeAt(0), b += wanakana.HIRAGANA_START - wanakana.KATAKANA_START, d = String.fromCharCode(b), c.push(d)) : c.push(e);
  return c.join("")
}, wanakana._hiraganaToKatakana = function(a) {
  var b, c, d, e, f, g, h;
  for (d = [], h = a.split(""), f = 0, g = h.length; g > f; f++) c = h[f], wanakana._isCharHiragana(c) ? (b = c.charCodeAt(0), b += wanakana.KATAKANA_START - wanakana.HIRAGANA_START, e = String.fromCharCode(b), d.push(e)) : d.push(c);
  return d.join("")
}, wanakana._hiraganaToRomaji = function(a, b) {
  var c, d, e, f, g, h, i, j, k, l;
  for (b = wanakana._extend(b, wanakana.defaultOptions), g = a.length, k = [], e = 0, d = 0, h = 2, f = function() {
      return a.substr(e, d)
    }, j = function() {
      return d = Math.min(h, g - e)
    }; g > e;) {
    for (j(); d > 0;) {
      if (c = f(), wanakana.isKatakana(c) && (c = wanakana._katakanaToHiragana(c)), "っ" === c.charAt(0) && 1 === d && g - 1 > e) {
        i = !0, l = "";
        break
      }
      if (l = wanakana.J_to_R[c], null != l && i && (l = l.charAt(0).concat(l), i = !1), null != l) break;
      d--
    }
    null == l && (l = c), k.push(l), e += d || 1
  }
  return k.join("")
}, wanakana._romajiToHiragana = function(a, b) {
  return wanakana._romajiToKana(a, b, !0)
}, wanakana._romajiToKana = function(a, b, c) {
  var d, e, f, g, h, i, j, k, l, m;
  for (null == c && (c = !1), b = wanakana._extend(b, wanakana.defaultOptions), l = a.length, j = [], g = 0, m = 3, h = function() {
      return a.substr(g, f)
    }, i = function(a) {
      return wanakana._isCharInRange(a, wanakana.UPPERCASE_START, wanakana.UPPERCASE_END)
    }; l > g;) {
    for (f = Math.min(m, l - g); f > 0;) {
      if (d = h(), e = d.toLowerCase(), __indexOf.call(wanakana.FOUR_CHARACTER_EDGE_CASES, e) >= 0 && l - g >= 4) f++, d = h(), e = d.toLowerCase();
      else {
        if ("n" === e.charAt(0)) {
          if (b.IMEMode && "'" === e.charAt(1) && 2 === f) {
            k = "ん";
            break
          }
          wanakana._isCharConsonant(e.charAt(1), !1) && wanakana._isCharVowel(e.charAt(2)) && (f = 1, d = h(), e = d.toLowerCase())
        }
        "n" !== e.charAt(0) && wanakana._isCharConsonant(e.charAt(0)) && d.charAt(0) === d.charAt(1) && (f = 1, e = d = wanakana._isCharInRange(d.charAt(0), wanakana.UPPERCASE_START, wanakana.UPPERCASE_END) ? "ッ" : "っ")
      }
      if (k = wanakana.R_to_J[e], null != k) break;
      4 === f ? f -= 2 : f--
    }
    null == k && (d = wanakana._convertPunctuation(d), k = d), (null != b ? b.useObseleteKana : void 0) && ("wi" === e && (k = "ゐ"), "we" === e && (k = "ゑ")), b.IMEMode && "n" === e.charAt(0) && ("y" === a.charAt(g + 1).toLowerCase() && wanakana._isCharVowel(a.charAt(g + 2)) === !1 || g === l - 1 || wanakana.isKana(a.charAt(g + 1))) && (k = d.charAt(0)), c || i(d.charAt(0)) && (k = wanakana._hiraganaToKatakana(k)), j.push(k), g += f || 1
  }
  return j.join("")
}, wanakana._convertPunctuation = function(a) {
  return "　" === a ? " " : "-" === a ? "ー" : a
}, wanakana.isHiragana = function(a) {
  var b;
  return b = a.split(""), b.every(wanakana._isCharHiragana)
}, wanakana.isKatakana = function(a) {
  var b;
  return b = a.split(""), b.every(wanakana._isCharKatakana)
}, wanakana.isKana = function(a) {
  var b;
  return b = a.split(""), b.every(function(a) {
    return wanakana.isHiragana(a) || wanakana.isKatakana(a)
  })
}, wanakana.isRomaji = function(a) {
  var b;
  return b = a.split(""), b.every(function(a) {
    return !wanakana.isHiragana(a) && !wanakana.isKatakana(a)
  })
}, wanakana.toHiragana = function(a, b) {
  return wanakana.isRomaji(a) ? a = wanakana._romajiToHiragana(a, b) : wanakana.isKatakana(a) ? a = wanakana._katakanaToHiragana(a, b) : a
}, wanakana.toKatakana = function(a, b) {
  return wanakana.isHiragana(a) ? a = wanakana._hiraganaToKatakana(a, b) : wanakana.isRomaji(a) ? (a = wanakana._romajiToHiragana(a, b), a = wanakana._hiraganaToKatakana(a, b)) : a
}, wanakana.toKana = function(a, b) {
  return a = wanakana._romajiToKana(a, b)
}, wanakana.toRomaji = function(a) {
  return a = wanakana._hiraganaToRomaji(a)
}, wanakana.R_to_J = {
  a: "あ",
  i: "い",
  u: "う",
  e: "え",
  o: "お",
  yi: "い",
  wu: "う",
  whu: "う",
  xa: "ぁ",
  xi: "ぃ",
  xu: "ぅ",
  xe: "ぇ",
  xo: "ぉ",
  xyi: "ぃ",
  xye: "ぇ",
  ye: "いぇ",
  wha: "うぁ",
  whi: "うぃ",
  whe: "うぇ",
  who: "うぉ",
  wi: "うぃ",
  we: "うぇ",
  va: "ゔぁ",
  vi: "ゔぃ",
  vu: "ゔ",
  ve: "ゔぇ",
  vo: "ゔぉ",
  vya: "ゔゃ",
  vyi: "ゔぃ",
  vyu: "ゔゅ",
  vye: "ゔぇ",
  vyo: "ゔょ",
  ka: "か",
  ki: "き",
  ku: "く",
  ke: "け",
  ko: "こ",
  lka: "ヵ",
  lke: "ヶ",
  xka: "ヵ",
  xke: "ヶ",
  kya: "きゃ",
  kyi: "きぃ",
  kyu: "きゅ",
  kye: "きぇ",
  kyo: "きょ",
  ca: "か",
  ci: "き",
  cu: "く",
  ce: "け",
  co: "こ",
  lca: "ヵ",
  lce: "ヶ",
  xca: "ヵ",
  xce: "ヶ",
  qya: "くゃ",
  qyu: "くゅ",
  qyo: "くょ",
  qwa: "くぁ",
  qwi: "くぃ",
  qwu: "くぅ",
  qwe: "くぇ",
  qwo: "くぉ",
  qa: "くぁ",
  qi: "くぃ",
  qe: "くぇ",
  qo: "くぉ",
  kwa: "くぁ",
  qyi: "くぃ",
  qye: "くぇ",
  ga: "が",
  gi: "ぎ",
  gu: "ぐ",
  ge: "げ",
  go: "ご",
  gya: "ぎゃ",
  gyi: "ぎぃ",
  gyu: "ぎゅ",
  gye: "ぎぇ",
  gyo: "ぎょ",
  gwa: "ぐぁ",
  gwi: "ぐぃ",
  gwu: "ぐぅ",
  gwe: "ぐぇ",
  gwo: "ぐぉ",
  sa: "さ",
  si: "し",
  shi: "し",
  su: "す",
  se: "せ",
  so: "そ",
  za: "ざ",
  zi: "じ",
  zu: "ず",
  ze: "ぜ",
  zo: "ぞ",
  ji: "じ",
  sya: "しゃ",
  syi: "しぃ",
  syu: "しゅ",
  sye: "しぇ",
  syo: "しょ",
  sha: "しゃ",
  shu: "しゅ",
  she: "しぇ",
  sho: "しょ",
  shya: "しゃ",
  shyu: "しゅ",
  shye: "しぇ",
  shyo: "しょ",
  swa: "すぁ",
  swi: "すぃ",
  swu: "すぅ",
  swe: "すぇ",
  swo: "すぉ",
  zya: "じゃ",
  zyi: "じぃ",
  zyu: "じゅ",
  zye: "じぇ",
  zyo: "じょ",
  ja: "じゃ",
  ju: "じゅ",
  je: "じぇ",
  jo: "じょ",
  jya: "じゃ",
  jyi: "じぃ",
  jyu: "じゅ",
  jye: "じぇ",
  jyo: "じょ",
  ta: "た",
  ti: "ち",
  tu: "つ",
  te: "て",
  to: "と",
  chi: "ち",
  tsu: "つ",
  ltu: "っ",
  xtu: "っ",
  tya: "ちゃ",
  tyi: "ちぃ",
  tyu: "ちゅ",
  tye: "ちぇ",
  tyo: "ちょ",
  cha: "ちゃ",
  chu: "ちゅ",
  che: "ちぇ",
  cho: "ちょ",
  cya: "ちゃ",
  cyi: "ちぃ",
  cyu: "ちゅ",
  cye: "ちぇ",
  cyo: "ちょ",
  chya: "ちゃ",
  chyu: "ちゅ",
  chye: "ちぇ",
  chyo: "ちょ",
  tsa: "つぁ",
  tsi: "つぃ",
  tse: "つぇ",
  tso: "つぉ",
  tha: "てゃ",
  thi: "てぃ",
  thu: "てゅ",
  the: "てぇ",
  tho: "てょ",
  twa: "とぁ",
  twi: "とぃ",
  twu: "とぅ",
  twe: "とぇ",
  two: "とぉ",
  da: "だ",
  di: "ぢ",
  du: "づ",
  de: "で",
  "do": "ど",
  dya: "ぢゃ",
  dyi: "ぢぃ",
  dyu: "ぢゅ",
  dye: "ぢぇ",
  dyo: "ぢょ",
  dha: "でゃ",
  dhi: "でぃ",
  dhu: "でゅ",
  dhe: "でぇ",
  dho: "でょ",
  dwa: "どぁ",
  dwi: "どぃ",
  dwu: "どぅ",
  dwe: "どぇ",
  dwo: "どぉ",
  na: "な",
  ni: "に",
  nu: "ぬ",
  ne: "ね",
  no: "の",
  nya: "にゃ",
  nyi: "にぃ",
  nyu: "にゅ",
  nye: "にぇ",
  nyo: "にょ",
  ha: "は",
  hi: "ひ",
  hu: "ふ",
  he: "へ",
  ho: "ほ",
  fu: "ふ",
  hya: "ひゃ",
  hyi: "ひぃ",
  hyu: "ひゅ",
  hye: "ひぇ",
  hyo: "ひょ",
  fya: "ふゃ",
  fyu: "ふゅ",
  fyo: "ふょ",
  fwa: "ふぁ",
  fwi: "ふぃ",
  fwu: "ふぅ",
  fwe: "ふぇ",
  fwo: "ふぉ",
  fa: "ふぁ",
  fi: "ふぃ",
  fe: "ふぇ",
  fo: "ふぉ",
  fyi: "ふぃ",
  fye: "ふぇ",
  ba: "ば",
  bi: "び",
  bu: "ぶ",
  be: "べ",
  bo: "ぼ",
  bya: "びゃ",
  byi: "びぃ",
  byu: "びゅ",
  bye: "びぇ",
  byo: "びょ",
  pa: "ぱ",
  pi: "ぴ",
  pu: "ぷ",
  pe: "ぺ",
  po: "ぽ",
  pya: "ぴゃ",
  pyi: "ぴぃ",
  pyu: "ぴゅ",
  pye: "ぴぇ",
  pyo: "ぴょ",
  ma: "ま",
  mi: "み",
  mu: "む",
  me: "め",
  mo: "も",
  mya: "みゃ",
  myi: "みぃ",
  myu: "みゅ",
  mye: "みぇ",
  myo: "みょ",
  ya: "や",
  yu: "ゆ",
  yo: "よ",
  xya: "ゃ",
  xyu: "ゅ",
  xyo: "ょ",
  ra: "ら",
  ri: "り",
  ru: "る",
  re: "れ",
  ro: "ろ",
  rya: "りゃ",
  ryi: "りぃ",
  ryu: "りゅ",
  rye: "りぇ",
  ryo: "りょ",
  la: "ら",
  li: "り",
  lu: "る",
  le: "れ",
  lo: "ろ",
  lya: "りゃ",
  lyi: "りぃ",
  lyu: "りゅ",
  lye: "りぇ",
  lyo: "りょ",
  wa: "わ",
  wo: "を",
  lwe: "ゎ",
  xwa: "ゎ",
  n: "ん",
  nn: "ん",
  "n ": "ん",
  xn: "ん",
  ltsu: "っ"
}, wanakana.FOUR_CHARACTER_EDGE_CASES = ["lts", "chy", "shy"], wanakana.J_to_R = {
  "あ": "a",
  "い": "i",
  "う": "u",
  "え": "e",
  "お": "o",
  "ゔぁ": "va",
  "ゔぃ": "vi",
  "ゔ": "vu",
  "ゔぇ": "ve",
  "ゔぉ": "vo",
  "か": "ka",
  "き": "ki",
  "きゃ": "kya",
  "きぃ": "kyi",
  "きゅ": "kyu",
  "く": "ku",
  "け": "ke",
  "こ": "ko",
  "が": "ga",
  "ぎ": "gi",
  "ぐ": "gu",
  "げ": "ge",
  "ご": "go",
  "ぎゃ": "gya",
  "ぎぃ": "gyi",
  "ぎゅ": "gyu",
  "ぎぇ": "gye",
  "ぎょ": "gyo",
  "さ": "sa",
  "す": "su",
  "せ": "se",
  "そ": "so",
  "ざ": "za",
  "ず": "zu",
  "ぜ": "ze",
  "ぞ": "zo",
  "し": "shi",
  "しゃ": "sha",
  "しゅ": "shu",
  "しょ": "sho",
  "じ": "ji",
  "じゃ": "ja",
  "じゅ": "ju",
  "じょ": "jo",
  "た": "ta",
  "ち": "chi",
  "ちゃ": "cha",
  "ちゅ": "chu",
  "ちょ": "cho",
  "つ": "tsu",
  "て": "te",
  "と": "to",
  "だ": "da",
  "ぢ": "di",
  "づ": "du",
  "で": "de",
  "ど": "do",
  "な": "na",
  "に": "ni",
  "にゃ": "nya",
  "にゅ": "nyu",
  "にょ": "nyo",
  "ぬ": "nu",
  "ね": "ne",
  "の": "no",
  "は": "ha",
  "ひ": "hi",
  "ふ": "fu",
  "へ": "he",
  "ほ": "ho",
  "ひゃ": "hya",
  "ひゅ": "hyu",
  "ひょ": "hyo",
  "ふぁ": "fa",
  "ふぃ": "fi",
  "ふぇ": "fe",
  "ふぉ": "fo",
  "ば": "ba",
  "び": "bi",
  "ぶ": "bu",
  "べ": "be",
  "ぼ": "bo",
  "びゃ": "bya",
  "びゅ": "byu",
  "びょ": "byo",
  "ぱ": "pa",
  "ぴ": "pi",
  "ぷ": "pu",
  "ぺ": "pe",
  "ぽ": "po",
  "ぴゃ": "pya",
  "ぴゅ": "pyu",
  "ぴょ": "pyo",
  "ま": "ma",
  "み": "mi",
  "む": "mu",
  "め": "me",
  "も": "mo",
  "みゃ": "mya",
  "みゅ": "myu",
  "みょ": "myo",
  "や": "ya",
  "ゆ": "yu",
  "よ": "yo",
  "ら": "ra",
  "り": "ri",
  "る": "ru",
  "れ": "re",
  "ろ": "ro",
  "りゃ": "rya",
  "りゅ": "ryu",
  "りょ": "ryo",
  "わ": "wa",
  "を": "wo",
  "ん": "n",
  "ゐ": "wi",
  "ゑ": "we",
  "きぇ": "kye",
  "きょ": "kyo",
  "じぃ": "jyi",
  "じぇ": "jye",
  "ちぃ": "cyi",
  "ちぇ": "che",
  "ひぃ": "hyi",
  "ひぇ": "hye",
  "びぃ": "byi",
  "びぇ": "bye",
  "ぴぃ": "pyi",
  "ぴぇ": "pye",
  "みぇ": "mye",
  "みぃ": "myi",
  "りぃ": "ryi",
  "りぇ": "rye",
  "にぃ": "nyi",
  "にぇ": "nye",
  "しぃ": "syi",
  "しぇ": "she",
  "いぇ": "ye",
  "うぁ": "wha",
  "うぉ": "who",
  "うぃ": "wi",
  "うぇ": "we",
  "ゔゃ": "vya",
  "ゔゅ": "vyu",
  "ゔょ": "vyo",
  "すぁ": "swa",
  "すぃ": "swi",
  "すぅ": "swu",
  "すぇ": "swe",
  "すぉ": "swo",
  "くゃ": "qya",
  "くゅ": "qyu",
  "くょ": "qyo",
  "くぁ": "qwa",
  "くぃ": "qwi",
  "くぅ": "qwu",
  "くぇ": "qwe",
  "くぉ": "qwo",
  "ぐぁ": "gwa",
  "ぐぃ": "gwi",
  "ぐぅ": "gwu",
  "ぐぇ": "gwe",
  "ぐぉ": "gwo",
  "つぁ": "tsa",
  "つぃ": "tsi",
  "つぇ": "tse",
  "つぉ": "tso",
  "てゃ": "tha",
  "てぃ": "thi",
  "てゅ": "thu",
  "てぇ": "the",
  "てょ": "tho",
  "とぁ": "twa",
  "とぃ": "twi",
  "とぅ": "twu",
  "とぇ": "twe",
  "とぉ": "two",
  "ぢゃ": "dya",
  "ぢぃ": "dyi",
  "ぢゅ": "dyu",
  "ぢぇ": "dye",
  "ぢょ": "dyo",
  "でゃ": "dha",
  "でぃ": "dhi",
  "でゅ": "dhu",
  "でぇ": "dhe",
  "でょ": "dho",
  "どぁ": "dwa",
  "どぃ": "dwi",
  "どぅ": "dwu",
  "どぇ": "dwe",
  "どぉ": "dwo",
  "ふぅ": "fwu",
  "ふゃ": "fya",
  "ふゅ": "fyu",
  "ふょ": "fyo",
  "ぁ": "a",
  "ぃ": "i",
  "ぇ": "e",
  "ぅ": "u",
  "ぉ": "o",
  "ゃ": "ya",
  "ゅ": "yu",
  "ょ": "yo",
  "っ": "",
  "ゕ": "ka",
  "ゖ": "ka",
  "ゎ": "wa",
  "　": " ",
  "んあ": "n'a",
  "んい": "n'i",
  "んう": "n'u",
  "んえ": "n'e",
  "んお": "n'o",
  "んや": "n'ya",
  "んゆ": "n'yu",
  "んよ": "n'yo"
};
