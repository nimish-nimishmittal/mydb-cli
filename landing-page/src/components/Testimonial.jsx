import React, { useEffect, useRef } from "react";
import { gsap } from "gsap";

const classNames = {
  container: "max-w-7xl mx-auto",
  header: "text-center",
  grid: "grid max-w-md mx-auto mt-12 sm:mt-16 lg:grid-cols-3 lg:max-w-none",
  card: "bg-gray-800 rounded-2xl p-8",
  footer:
    "flex items-center justify-between pt-5 mt-5 border-t border-gray-700",
};

const testimonials = [
  {
    quote:
      '"DbCli has completely transformed the way we manage our databases. The commands are intuitive and help streamline our workflow."',
    name: "Bessie Cooper",
    role: "Co-Founder, CEO",
    logoSrc: (
      <h1 className="text-xl font-medium text-white transition-all duration-200 hover:text-indigo-600">
        DbCli
      </h1>
    ), // Using h1 for the logo in all testimonials
    avatarSrc: "https://www.auraUI.com/memeimage/man1.jpg",
  },
  {
    quote:
      '"With DbCli, managing database migrations and branches became incredibly easy. It\'s a game-changer for our development team."',
    name: "Albert Flores",
    role: "Senior Product Manager",
    logoSrc: (
      <h1 className="text-xl font-medium text-white transition-all duration-200 hover:text-indigo-600">
        DbCli
      </h1>
    ), // Using h1 for the logo in all testimonials
    avatarSrc: "https://www.auraUI.com/memeimage/woman1.jpg",
  },
  {
    quote:
      '"DbCli has been instrumental in improving our database management. Our processes are more streamlined, and we\'ve seen significant improvements."',
    name: "Jenny Wilson",
    role: "Head of Marketing",
    logoSrc: (
      <h1 className="text-xl font-medium text-white transition-all duration-200 hover:text-indigo-600">
        DbCli
      </h1>
    ), // Using h1 for the logo in all testimonials
    avatarSrc: "https://www.auraUI.com/memeimage/woman2.jpg",
  },
];

function Testimonial2() {
  const gridRef = useRef(null);
  const cardsRef = useRef([]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Animate cards when the section enters the viewport
            const ctx = gsap.context(() => {
              gsap.fromTo(
                cardsRef.current,
                {
                  opacity: 0,
                  scale: 0.5,
                  y: 50,
                },
                {
                  opacity: 1,
                  scale: 1,
                  y: 0,
                  duration: 1,
                  stagger: 0.2,
                  ease: "power3.out",
                  delay: 0.3,
                }
              );
              gsap.to(gridRef.current, {
                autoAlpha: 1,
                duration: 1,
                delay: 0.2,
              });
            }, gridRef);
            observer.disconnect(); // Stop observing once the animation is triggered
          }
        });
      },
      {
        threshold: 0.2, // Trigger animation when 20% of the section is in view
      }
    );

    if (gridRef.current) {
      observer.observe(gridRef.current); // Start observing the grid element
    }

    return () => {
      if (gridRef.current) {
        observer.unobserve(gridRef.current); // Cleanup on component unmount
      }
    };
  }, []);

  return (
    <section className="py-12 bg-black sm:py-16 lg:py-20 xl:py-24">
      <div className={`px-4 sm:px-6 lg:px-8 ${classNames.container}`}>
        <div className={`max-w-3xl mx-auto ${classNames.header}`}>
          <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl lg:text-5xl">
            Don&apos;t just take our words. Over 1000+ people trust us.
          </h2>
        </div>

        <div
          ref={gridRef}
          className={`grid-cols-1 gap-5 ${classNames.grid}`}
        >
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              ref={(el) => (cardsRef.current[index] = el)}
              className={`${classNames.card} ${
                index % 2 === 0 ? "xl:-rotate-2" : "xl:rotate-2"
              }`}
            >
              <blockquote>
                <p className="text-xl font-medium leading-9 text-white">
                  {testimonial.quote}
                </p>
              </blockquote>
              <p className="mt-6 text-base font-semibold text-white">
                {testimonial.name}
              </p>
              <p className="mt-1 text-base font-normal text-gray-400">
                {testimonial.role}
              </p>
              <div className={classNames.footer}>
                {/* Render logoSrc as JSX (h1 in all cases) */}
                {testimonial.logoSrc}
                <img
                  className="object-cover w-10 h-10 rounded-full"
                  src={testimonial.avatarSrc}
                  alt={`${testimonial.name} avatar`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Testimonial2;
