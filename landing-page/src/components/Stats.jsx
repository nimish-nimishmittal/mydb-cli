import React, { useEffect, useRef } from "react";
import { gsap } from "gsap";

const styles = {
  section: "py-12 bg-black sm:py-16 lg:py-20 xl:py-24", // Black background for section
  container: "px-4 mx-auto sm:px-6 lg:px-8 max-w-7xl",
  headerContainer: "max-w-xl mx-auto text-center",
  headerTitle: "text-3xl font-semibold tracking-tight text-white sm:text-4xl lg:text-5xl", // White text for title
  headerSubtitle: "mt-4 text-base font-normal leading-7 text-white lg:text-lg lg:mt-6 lg:leading-8", // White text for subtitle
  achievementsContainer: "relative max-w-2xl mx-auto mt-12 overflow-hidden bg-gradient-to-r from-purple-500 to-blue-500 sm:mt-16 lg:max-w-3xl xl:max-w-none rounded-2xl",
  circleDecoration: "border-[8px] border-white rounded-full w-80 h-80 opacity-20 lg:opacity-100", // White border for circles
  circleLeft: "absolute top-0 left-0 -translate-x-2/3 -translate-y-[75%]",
  circleRight: "absolute bottom-0 right-0 translate-x-1/3 translate-y-[85%]",
  content: "relative px-8 py-12 lg:px-12 lg:py-16 xl:py-20",
  grid: "grid grid-cols-1 gap-8 xl:gap-8 sm:grid-cols-2 xl:grid-cols-4",
  achievementItem: "flex items-center",
  achievementNumber: "w-24 text-5xl font-semibold tracking-tight text-white xl:w-auto shrink-0", // White text for numbers
  achievementText: "ml-5 text-base font-normal leading-tight text-white", // White text for description
};

const achievements = [
  { number: "483", text: "Satisfied database users" },
  { number: "78%", text: "Migration success rate" },
  { number: "854", text: "Database migrations completed" },
  { number: "315", text: "Database branches created" },
];

const Stats = () => {
  const numbersRef = useRef([]);

  useEffect(() => {
    // Animate number increment from 0 to the target number
    numbersRef.current.forEach((el, index) => {
      const targetNumber = parseInt(achievements[index].number.replace("%", ""));
      gsap.fromTo(
        el,
        { innerText: 0 },
        {
          innerText: targetNumber,
          duration: 2,
          ease: "power2.out",
          snap: { innerText: 1 },
          stagger: 0.2,
        }
      );
    });
  }, []);

  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.headerContainer}>
          <h2 className={styles.headerTitle}>Our achievements</h2>
          <p className={styles.headerSubtitle}>
            DbCli provides the commands and tools you need to efficiently manage and optimize your databases, making it the perfect solution for teams working with MySQL databases.
          </p>
        </div>

        <div className={styles.achievementsContainer}>
          <div className={`${styles.circleDecoration} ${styles.circleLeft}`}></div>
          <div className={`${styles.circleDecoration} ${styles.circleRight}`}></div>

          <div className={styles.content}>
            <div className={styles.grid}>
              {achievements.map((achievement, index) => (
                <div key={index} className={styles.achievementItem}>
                  <p
                    className={styles.achievementNumber}
                    ref={(el) => (numbersRef.current[index] = el)} // Assign refs to each achievement number
                  >
                    {achievement.number}
                  </p>
                  <h3 className={styles.achievementText}>{achievement.text}</h3>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Stats;
