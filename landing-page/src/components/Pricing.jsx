import React, { useEffect, useRef } from "react";
import { gsap } from "gsap";
import {
  FaCheckCircle,
  FaCloud,
  FaRegHandshake,
  FaPlug,
  FaBox,
} from "react-icons/fa";
import { IoMdStar, IoMdPeople } from "react-icons/io";

const commonStyles =
  "flex items-center text-base font-medium text-white font-pj";
const iconStyles = "w-5 h-5 mr-2";

const gradientStyles = {
  background:
    "linear-gradient(90deg, #44ff9a -0.55%, #44b0ff 22.86%, #8b44ff 48.36%, #ff6644 73.33%, #ebff70 99.34%)",
};

const Pricing = () => {
  const pricingRef = useRef(null);
  const featureListRef = useRef([]);
  const priceRef = useRef(null);
  const ctaRef = useRef(null);
  const testimonialRef = useRef(null);

  useEffect(() => {
    const options = {
      root: null, // use the viewport as the root
      rootMargin: "0px", // no margin
      threshold: 0.5, // trigger when 50% of the element is in view
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // Animate the pricing section when it comes into view
          gsap.fromTo(
            pricingRef.current,
            { opacity: 0, y: 50 },
            { opacity: 1, y: 0, duration: 1, ease: "power3.out" }
          );

          // Animate the feature list items
          featureListRef.current.forEach((item, index) => {
            gsap.fromTo(
              item,
              { opacity: 0, x: -20 },
              { opacity: 1, x: 0, duration: 0.6, delay: index * 0.1, ease: "power3.out" }
            );
          });

          // Animate the price and CTA
          gsap.fromTo(
            [priceRef.current, ctaRef.current],
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.8, delay: 0.5, stagger: 0.2, ease: "power3.out" }
          );

          // Animate the testimonial section
          gsap.fromTo(
            testimonialRef.current,
            { opacity: 0, y: 50 },
            { opacity: 1, y: 0, duration: 0.8, delay: 1, ease: "power3.out" }
          );

          // Unobserve once the animations are triggered
          observer.unobserve(entry.target);
        }
      });
    }, options);

    if (pricingRef.current) {
      observer.observe(pricingRef.current);
    }

    return () => {
      if (pricingRef.current) {
        observer.unobserve(pricingRef.current);
      }
    };
  }, []);

  return (
    <section className="py-12 bg-black sm:py-16 lg:py-20" ref={pricingRef}>
      <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl xl:text-5xl font-pj">
            All features for one price. Experience DbCli for free!
          </h2>
        </div>

        <div className="relative max-w-5xl mx-auto mt-8 md:mt-16">
          <div className="absolute inset-0">
            <div
              className="w-full h-full mx-auto opacity-30 blur-lg filter"
              style={gradientStyles}
            ></div>
          </div>

          <div className="relative overflow-hidden bg-black rounded-2xl">
            <div className="px-16 py-8 sm:px-8 lg:px-16 lg:py-14">
              <div className="md:flex md:items-center md:space-x-12 lg:space-x-24">
                <div className="grid grid-cols-1 gap-y-3 sm:grid-cols-2 gap-x-12 xl:gap-x-24">
                  <div>
                    <ul className="space-y-3" ref={(el) => (featureListRef.current[0] = el)}>
                      <li className={commonStyles}>
                        <FaCheckCircle className={iconStyles} />
                        Unlimited database commands
                      </li>
                      <li className={commonStyles} ref={(el) => (featureListRef.current[1] = el)}>
                        <IoMdPeople className={iconStyles} />3 admin database branches
                      </li>
                      <li className={commonStyles} ref={(el) => (featureListRef.current[2] = el)}>
                        <FaCloud className={iconStyles} />
                        100GB database storage
                      </li>
                    </ul>
                  </div>

                  <div>
                    <ul className="space-y-3" ref={(el) => (featureListRef.current[3] = el)}>
                      <li className={commonStyles}>
                        <FaPlug className={iconStyles} />
                        Custom database branches
                      </li>
                      <li className={commonStyles} ref={(el) => (featureListRef.current[4] = el)}>
                        <FaBox className={iconStyles} />
                        Migration API access
                      </li>
                      <li className={commonStyles} ref={(el) => (featureListRef.current[5] = el)}>
                        <FaRegHandshake className={iconStyles} />
                        Bulk database importer
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="mt-10 md:mt-0">
                  <div className="flex items-end" ref={priceRef}>
                    <p className="text-5xl font-bold text-white font-pj">$19</p>
                    <p className="text-lg font-medium text-gray-400 font-pj">
                      /month
                    </p>
                  </div>

                  <a
                    href="#"
                    className="inline-flex items-center justify-center px-9 py-3.5 mt-5 text-base font-bold text-black transition-all duration-200 bg-white border border-transparent focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white font-pj hover:bg-opacity-90 rounded-xl"
                    ref={ctaRef}
                  >
                    Get started now
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-2xl mx-auto mt-12 text-center sm:mt-16 sm:flex sm:items-start sm:justify-center sm:text-left" ref={testimonialRef}>
          <img
            className="flex-shrink-0 object-cover mx-auto rounded-full w-28 h-28 sm:mx-0"
            src="https://www.auraui.com/memeimage/man1.jpg"
            alt="AuraUI user"
          />
          <div className="mt-6 sm:mt-0 sm:ml-12">
            <blockquote>
              <p className="text-lg font-normal leading-relaxed text-white font-pj">
              "DbCli has transformed the way we manage our databases. The intuitive commands and powerful features make it an essential tool for our team." "AuraUI has transformed the way we manage our projects. The
                intuitive design and extensive features make it an essential
                tool for our team."
              </p>
            </blockquote>
            <p className="mt-5 text-base font-bold text-white font-pj">
             Atharva Tikle
            </p>
            <p className="text-sm font-normal text-gray-400 font-pj mt-0.5">
              CTO, DbCli
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
