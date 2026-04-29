import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Icosahedron, Sphere, Trail } from "@react-three/drei";
import * as THREE from "three";

function Orbiter({ radius, speed, color, size = 0.05, offset = 0 }: { radius: number; speed: number; color: string; size?: number; offset?: number }) {
  const ref = useRef<THREE.Mesh>(null!);
  useFrame((state) => {
    const t = state.clock.elapsedTime * speed + offset;
    ref.current.position.set(Math.cos(t) * radius, Math.sin(t * 0.7) * radius * 0.4, Math.sin(t) * radius);
  });
  return (
    <Trail width={0.6} length={6} color={color} attenuation={(t) => t * t}>
      <Sphere ref={ref} args={[size, 16, 16]}>
        <meshBasicMaterial color={color} toneMapped={false} />
      </Sphere>
    </Trail>
  );
}

function Particles({ count = 800 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null!);
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 2.5 + Math.random() * 4;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, [count]);
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y = state.clock.elapsedTime * 0.04;
      ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
    }
  });
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.025} color="#7dd3fc" transparent opacity={0.7} sizeAttenuation depthWrite={false} />
    </points>
  );
}

function Core() {
  const mesh = useRef<THREE.Mesh>(null!);
  const wire = useRef<THREE.Mesh>(null!);
  useFrame((state) => {
    const t = state.clock.elapsedTime;
    mesh.current.rotation.x = t * 0.2;
    mesh.current.rotation.y = t * 0.25;
    wire.current.rotation.x = -t * 0.15;
    wire.current.rotation.y = -t * 0.2;
    const s = 1 + Math.sin(t * 1.6) * 0.04;
    mesh.current.scale.setScalar(s);
  });
  return (
    <group>
      <Icosahedron ref={mesh} args={[1.1, 1]}>
        <meshStandardMaterial
          color="#0ea5e9"
          emissive="#22d3ee"
          emissiveIntensity={1.4}
          roughness={0.3}
          metalness={0.6}
          flatShading
        />
      </Icosahedron>
      <Icosahedron ref={wire} args={[1.45, 2]}>
        <meshBasicMaterial color="#a855f7" wireframe transparent opacity={0.35} toneMapped={false} />
      </Icosahedron>
      <Sphere args={[0.55, 32, 32]}>
        <meshBasicMaterial color="#e0f2fe" toneMapped={false} transparent opacity={0.85} />
      </Sphere>
    </group>
  );
}

export const NeuralCore = ({ compact = false }: { compact?: boolean }) => {
  const group = useRef<THREE.Group>(null!);
  useFrame((state) => {
    if (!group.current) return;
    const { x, y } = state.pointer;
    group.current.rotation.y += (x * 0.4 - group.current.rotation.y) * 0.04;
    group.current.rotation.x += (-y * 0.25 - group.current.rotation.x) * 0.04;
  });
  return (
    <group ref={group} scale={compact ? 0.7 : 1}>
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={2} color="#22d3ee" />
      <pointLight position={[-5, -3, -2]} intensity={1.5} color="#a855f7" />
      <Core />
      <Orbiter radius={2.2} speed={0.9} color="#22d3ee" />
      <Orbiter radius={2.6} speed={0.7} color="#3b82f6" offset={2} />
      <Orbiter radius={3.0} speed={0.5} color="#a855f7" offset={4} />
      <Orbiter radius={2.4} speed={1.2} color="#67e8f9" size={0.04} offset={1} />
      <Particles />
    </group>
  );
};