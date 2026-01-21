import { useNavigate } from 'react-router-dom';
import { FileAudio, Bot, ArrowRight, CheckCircle, Sparkles, Mic, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';

const features = [
  {
    icon: FileAudio,
    title: 'AI Transcription',
    description: 'Automatic speech-to-text using local Whisper models for complete privacy.',
  },
  {
    icon: Sparkles,
    title: 'Smart Summaries',
    description: 'Extract key points, decisions, deadlines, and action items.',
  },
  {
    icon: Mic,
    title: 'Speaker Recognition',
    description: 'Train voice profiles to automatically identify who said what.',
  },
  {
    icon: Search,
    title: 'RAG Chatbot',
    description: 'Ask questions and get answers from your entire meeting history.',
  },
];

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-hero" />
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-40 left-1/4 w-96 h-96 rounded-full bg-primary blur-3xl" />
          <div className="absolute bottom-20 right-1/4 w-80 h-80 rounded-full bg-primary/50 blur-3xl" />
        </div>

        <nav className="absolute top-0 left-0 right-0 z-20 container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-primary shadow-glow">
                <FileAudio className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-primary-foreground">ClariMeet</span>
            </div>
            <Button
              variant="outline"
              onClick={() => navigate('/login')}
              className="border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10 hover:border-primary-foreground/50"
            >
              Sign In
            </Button>
          </div>
        </nav>
        
        <div className="relative z-10 container mx-auto px-6 pt-32 pb-24 lg:pt-40 lg:pb-32">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary/20 px-4 py-2 mb-8">
              <Bot className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">100% Local & Private</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-primary-foreground leading-tight mb-6">
              Transform Meetings into
              <span className="text-gradient block mt-2">Actionable Insights</span>
            </h1>
            
            <p className="text-lg md:text-xl text-primary-foreground/70 mb-10 max-w-2xl mx-auto">
              AI-powered meeting minutes with automatic transcription, smart summaries, 
              and an intelligent chatbot to query your entire meeting history.
            </p>

            {/* View Demo Button Removed Below */}
            <div className="flex items-center justify-center">
              <Button
                variant="hero"
                size="xl"
                onClick={() => navigate('/login')}
                className="w-full sm:w-auto"
              >
                Get Started
                <ArrowRight className="h-5 w-5" />
              </Button>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6 md:gap-8 mt-12">
              <div className="flex items-center gap-2 text-primary-foreground/60">
                <CheckCircle className="h-5 w-5 text-primary" />
                <span className="text-sm">No cloud required</span>
              </div>
              <div className="flex items-center gap-2 text-primary-foreground/60">
                <CheckCircle className="h-5 w-5 text-primary" />
                <span className="text-sm">100% free & open source</span>
              </div>
              <div className="flex items-center gap-2 text-primary-foreground/60">
                <CheckCircle className="h-5 w-5 text-primary" />
                <span className="text-sm">Self-hosted</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Everything You Need for Meeting Intelligence
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Built with privacy-first architecture using local AI models
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative rounded-2xl border border-border bg-card p-8 hover:shadow-lg hover:border-primary/30 transition-all duration-300"
            >
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-accent mb-6 group-hover:bg-gradient-primary group-hover:shadow-glow transition-all duration-300">
                <feature.icon className="h-7 w-7 text-primary group-hover:text-primary-foreground transition-colors" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-6 pb-24">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-hero p-12 md:p-16">
          <div className="absolute inset-0 opacity-20">
            <div className="absolute top-10 right-10 w-64 h-64 rounded-full bg-primary blur-3xl" />
          </div>
          <div className="relative z-10 max-w-2xl">
            <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
              Ready to automate your meeting notes?
            </h2>
            <p className="text-lg text-primary-foreground/70 mb-8">
              Connect your local Whisper and Ollama instance to get started with AI-powered meeting minutes.
            </p>
            <Button
              variant="hero"
              size="lg"
              onClick={() => navigate('/login')}
            >
              Start Free Today
              <ArrowRight className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileAudio className="h-5 w-5 text-primary" />
            <span className="font-semibold text-foreground">ClariMeet</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Open source · Privacy first · Built with ❤️
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;