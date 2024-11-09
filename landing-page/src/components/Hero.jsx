import React, { useState, useEffect } from "react";
import { HiOutlineBars3 } from "react-icons/hi2";
import { RxCross2 } from "react-icons/rx";
import { gsap } from "gsap";
import LoginButton from "./auth/Button/LoginButton";

function Hero() {
  const [expanded, setExpanded] = useState(false);

  const commonClasses = {
    navLink:
      "text-base font-medium text-white transition-all duration-200 hover:text-indigo-400",
    articleLink:
      "overflow-hidden transition-all duration-200 transform bg-black border border-gray-800 rounded-2xl hover:shadow-lg hover:-translate-y-1",
    button:
      "inline-flex relative items-center justify-center w-full sm:w-auto px-8 py-3 sm:text-sm text-base sm:py-3.5 font-semibold text-black transition-all duration-200 bg-white border border-transparent rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white",
  };

  const navLinks = ["Features", "Pricing", "Support"];
  const articles = [
    {
      title: "Boost your database design workflow with DbCli",
      category: "Design",
      date: "August 21, 2024",
      imgSrc: "https://www.auraUi.com/memeimage/woman1.jpg",
    },
    {
      title: "The future of component libraries with DbCli",
      category: "Development",
      date: "August 19, 2024",
      imgSrc: "https://www.auraUI.com/memeimage/hero8.jpg",
    },
    {
      title: "How DbCli enhances Database design",
      category: "Database",
      date: "August 18, 2024",
      imgSrc: "https://www.auraUI.com/memeimage/laptop-working-men.jpg",
    },
  ];

  useEffect(() => {
    // Hero Section Animations
    gsap.fromTo(
      ".hero-title",
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0, duration: 1, ease: "power4.out" }
    );

    gsap.fromTo(
      ".hero-description",
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 1, delay: 0.3, ease: "power4.out" }
    );

    gsap.fromTo(
      ".hero-button",
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 1, delay: 0.5, ease: "power4.out" }
    );

    gsap.fromTo(
      ".hero-image",
      { opacity: 0, scale: 0.8 },
      { opacity: 1, scale: 1, duration: 1, delay: 0.7, ease: "power4.out" }
    );

    // Animating articles with stagger
    gsap.fromTo(
      ".article-link",
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 1, stagger: 0.3, ease: "power3.out" }
    );

    // Parallax effect for the background image
    gsap.to(".hero-image", {
      yPercent: -20,
      scrollTrigger: {
        trigger: ".hero-image",
        start: "top bottom",
        end: "bottom top",
        scrub: true,
      },
    });
  }, []);

  return (
    <div className="relative bg-black text-white">
      <header className="absolute inset-x-0 top-0 z-10 py-4 bg-transparent sm:py-5">
        <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <nav className="flex items-center justify-between">
            <div className="flex shrink-0">
              <a href="#" title="DbCli" className="flex">
                <h1 className="text-xl font-medium text-white transition-all duration-200 hover:text-indigo-400">DbCli</h1>
              </a>
            </div>

            <div className="flex md:hidden">
              <button
                type="button"
                className="text-white"
                onClick={() => setExpanded(!expanded)}
                aria-expanded={expanded}
              >
                {!expanded ? (
                  <HiOutlineBars3 className="w-7 h-7" />
                ) : (
                  <RxCross2 className="w-7 h-7" />
                )}
              </button>
            </div>

            <div className="hidden md:flex md:items-center md:justify-start md:ml-16 md:mr-auto md:space-x-10">
              {navLinks.map((link) => (
                <a href="#" key={link} className={commonClasses.navLink}>
                  {link}
                </a>
              ))}
              <LoginButton />
            </div>
          </nav>

          {expanded && (
            <nav className="px-1 pt-8 pb-4">
              <div className="grid gap-y-6">
                {navLinks.map((link) => (
                  <a href="#" key={link} className={commonClasses.navLink}>
                    {link}
                  </a>
                ))}
                <LoginButton />
              </div>
            </nav>
          )}
        </div>
      </header>

      <section className="relative bg-black text-white">
        <div className="absolute inset-0">
          <div className="absolute inset-y-0 left-0 w-1/2 bg-black"></div>
        </div>

        <div className="relative mx-auto max-w-7xl lg:grid lg:grid-cols-2">
          <div className="flex justify-center items-center px-4 pb-16 pt-28 sm:px-6 lg:px-8 lg:pb-24 xl:pr-12">
            <div className="max-w-lg mx-auto lg:mx-0">
              <p className="hero-title text-5xl sm:text-6xl lg:text-7xl">⚡️</p>
              <h1 className="hero-title mt-10 text-3xl font-bold  sm:text-4xl lg:text-5xl text-white">
                Accelerate Your Database with DbCli.
              </h1>
              <p className="hero-description mt-6 text-base font-normal leading-7 text-gray-400">
                Unleash the power of db-cli to streamline your database management, making branching and migrations effortless for developers.
              </p>
              <div className="relative inline-flex mt-10 group">
                <div className="absolute transition-all duration-1000 opacity-70 inset-0 bg-gradient-to-r from-[#44BCFF] via-[#FF44EC] to-[#FF675E] rounded-xl blur-lg filter group-hover:opacity-100 group-hover:duration-200"></div>
                <a href="#" className={`${commonClasses.button} hero-button`}>
                  Read Exclusive Insights
                </a>
              </div>
            </div>
          </div>

          <div className="relative flex items-end px-4 py-16 bg-black sm:px-6 lg:pb-24 lg:px-8 xl:pl-12">
            <div className="absolute inset-0">
              <img
                className="hero-image object-cover w-full h-full"
                src="https://www.auraUI.com/memeimage/grid-pattern.svg"
                alt="Grid Pattern"
              />
            </div>

            <div className="relative w-full max-w-lg mx-auto lg:max-w-none">
              <p className="text-lg font-bold text-white">Featured Articles</p>

              <div className="mt-6 space-y-5">
                {articles.map(({ title, category, date, imgSrc }, index) => (
                  <div key={index} className={`${commonClasses.articleLink} article-link`}>
                    <div className="px-4 py-5 sm:p-5">
                      <div className="flex items-start lg:items-center">
                        <a href="#" title={title} className="shrink-0">
                          <img
                            className="lg:h-24 w-14 h-14 lg:w-24 rounded-xl object-cover"
                            src={imgSrc}
                            alt={title}
                          />
                        </a>

                        <div className="flex-1 ml-4 lg:ml-6">
                          <p className="text-xs font-medium text-white lg:text-sm">
                            {category}
                          </p>
                          <p className="mt-1 text-sm font-semibold text-white">
                            <a href="#" className="hover:text-gray-300">
                              {title}
                            </a>
                          </p>
                          <p className="mt-1 text-sm text-gray-400">{date}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Hero;
