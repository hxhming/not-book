// 修复 Create 流体储罐配方：把原版木桶替换成 TFC 木桶
// 放置位置：.minecraft/kubejs/server_scripts/fluid_tank_fix.js
ServerEvents.recipes(event => {
  // 移除 Create 原版流体储罐配方（那个用了原版木桶、在 TFC 里合成不了的死配方）
  event.remove({ id: 'create:crafting/kinetics/fluid_tank' })

  // 用 TFC 木桶重写
  // C = TFC 铜板（走 tag，自动匹配 TFC 铜板）
  // B = TFC 木桶
  event.shaped('create:fluid_tank', [
    'C C',
    'CBC',
    'C C'
  ], {
    C: '#forge:plates/copper',
    B: 'tfc:barrel'
  })
})
