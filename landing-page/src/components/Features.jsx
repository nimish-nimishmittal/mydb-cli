import React, { useEffect, useRef } from "react";
import { FaUsers, FaRocket } from "react-icons/fa";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const commonStyles = "text-gray-200 h-11 w-11"; // Icon styling

const features = [
  {
    icon: <FaUsers className={commonStyles} />,
    title: "DbCli Community",
    description:
      "Join the vibrant db-cli community, where developers collaborate to manage and optimize MySQL databases with advanced features.",
  },
  {
    icon: <FaRocket className={commonStyles} />,
    title: "Rapid Development",
    description:
      "Accelerate your database management process with db-cli's optimized commands for migrations, branching, and table management.",
  },
  {
    icon: <FaUsers className={commonStyles} />,
    title: "Collaborative Projects",
    description:
      "Work with team members on different database branches and contribute to streamlined project management with db-cli.",
  },
  {
    icon: <FaRocket className={commonStyles} />,
    title: "Innovative Tools",
    description:
      "Utilize db-cli's innovative tools for efficient database migrations, branch switching, and table management in MySQL.",
  },
];

function Feature() {
  const featureRef = useRef(null); // Reference for feature section
  const cardsRef = useRef([]); // Reference to each feature card for animation

  useEffect(() => {
    // GSAP animation for the entire feature section coming from the left
    gsap.fromTo(
      featureRef.current,
      {
        opacity: 0,
        x: -100, // Start off-screen to the left
      },
      {
        opacity: 1,
        x: 0,
        duration: 1.5, // Longer duration for smooth transition
        ease: "power3.out", // Smoother easing
        scrollTrigger: {
          trigger: featureRef.current,
          start: "top 75%", // Trigger when the section reaches 75% of the viewport height
          end: "bottom 25%",
          scrub: true, // Allows smoother scrolling effect
        },
      }
    );

    // Animate each card with stagger and easing
    cardsRef.current.forEach((card, index) => {
      gsap.fromTo(
        card,
        {
          opacity: 0,
          y: 100, // Start position (from below)
        },
        {
          opacity: 1,
          y: 0,
          duration: 1.2,
          delay: index * 0.2, // Stagger each card animation for smooth effect
          ease: "power3.out", // Smoother easing for card animation
          scrollTrigger: {
            trigger: card,
            start: "top 80%",
            end: "bottom 20%",
            scrub: true,
          },
        }
      );
    });
  }, []);

  return (
    <section
      id="features"
      className="py-12 sm:py-16 lg:py-20 bg-black" // Set background to pure black
      ref={featureRef} // Attach ref to the section for scroll-triggered animation
    >
      <div className="px-6 mx-auto sm:px-8 lg:px-12 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-x-16 xl:gap-x-32 gap-y-12">
          <div>
            <h2 className="tracking-tighter text-white"> {/* Text in white */}
              <span className="font-sans text-4xl md:text-6xl">
                Accelerate Your Database with
              </span>
              <span className="font-serif text-5xl italic md:block md:text-7xl">
                DbCli
              </span>
            </h2>
            <p className="mt-8 font-sans text-lg font-normal leading-8 text-gray-400"> {/* Light gray text */}
              DbCli provides a suite of powerful and efficient commands, enabling
              developers to manage and optimize MySQL databases with ease, from
              branching and migrations to table management.
            </p>
            <div className="mt-8">
              <a
                href="#"
                title="Watch trailer"
                className="inline-flex items-center justify-center px-5 py-2 font-sans text-base font-semibold transition-all duration-200 bg-gray-700 text-white border-2 rounded-full sm:leading-8 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-700 sm:text-lg"
                role="button"
              >
                <FaRocket className="w-6 h-6 mr-2" />
                Watch trailer
              </a>
            </div>
          </div>

          <div>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="feature-card space-y-5 overflow-hidden transition-all duration-200 border rounded-lg border-gray-700 bg-gray-900 hover:bg-gray-800" // Set background to pure black and hover effect
                  ref={(el) => (cardsRef.current[index] = el)} // Attach ref to each card for animation
                >
                  <div className="px-4 py-5 sm:p-6 lg:p-8">
                    {feature.icon}
                    <h3 className="mt-3 font-sans text-2xl font-normal text-white"> {/* White text for titles */}
                      {feature.title}
                    </h3>
                    <p className="mt-4 text-base font-normal text-gray-400"> {/* Light gray text */}
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Feature;
