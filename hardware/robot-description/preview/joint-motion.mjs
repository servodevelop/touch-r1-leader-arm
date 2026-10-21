// 仅根据 URDF 的 mimic 关系计算从动关节，避免预览另设一套联动规则。
export function resolveJointAngles(joints, inputs = {}) {
  const byName = new Map(joints.map(j => [j.name, j]));
  const result = new Map(), visiting = new Set();
  function resolve(name) {
    if (result.has(name)) return result.get(name);
    if (!byName.has(name)) throw Error(`联动源关节不存在：${name}`);
    if (visiting.has(name)) throw Error(`关节联动存在循环：${name}`);
    visiting.add(name);
    const joint = byName.get(name);
    const value = joint.mimic
      ? resolve(joint.mimic.joint) * joint.mimic.multiplier + joint.mimic.offset
      : (inputs[name] ?? 0);
    if (!Number.isFinite(value)) throw Error(`关节角度无效：${name}`);
    result.set(name, value); visiting.delete(name);
    return value;
  }
  for (const joint of joints) resolve(joint.name);
  return result;
}
