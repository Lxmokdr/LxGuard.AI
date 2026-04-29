import { Nav } from "@/components/lx/Nav";
import { Hero } from "@/components/sections/Hero";
import { Architecture } from "@/components/sections/Architecture";
import { Pipeline } from "@/components/sections/Pipeline";
import { Modes } from "@/components/sections/Modes";
import { Security } from "@/components/sections/Security";
import { TechStack } from "@/components/sections/TechStack";
import { Ingestion } from "@/components/sections/Ingestion";
import { Footer } from "@/components/sections/Footer";
import { ScrollToTop } from "@/components/lx/ScrollToTop";

const Index = () => {
  return (
    <main className="relative min-h-screen overflow-x-clip bg-background text-foreground">
      <Nav />
      <Hero />
      <Architecture />
      <Modes />
      <Security />
      <Ingestion />
      <TechStack />
      <Footer />
      <ScrollToTop />
    </main>
  );
};

export default Index;
